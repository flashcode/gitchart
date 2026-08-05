# SPDX-FileCopyrightText: 2026 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures for Gitchart tests."""

import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import IO, Any, NamedTuple

import pygal
import pytest

from gitchart.cli import main
from gitchart.gitchart import GitChart


class Commit(NamedTuple):
    """A commit to create in the test git repository."""

    date: str
    author: str
    subject: str
    path: str
    tag: str = ""


# commits created on the main branch of the test repository
COMMITS: tuple[Commit, ...] = (
    Commit("2013-03-15T18:27:55+01:00", "Alice", "Initial commit", "main.c"),
    Commit("2013-03-16T09:10:00+01:00", "Alice", "Add feature, fixes #12", "util.c", "v0.1"),
    Commit("2013-04-02T14:05:00+01:00", "Bob", "Fix bug, closes #34", "README.md", "v1.0"),
    Commit("2014-01-05T22:45:00+01:00", "Bob", "Refactor, fixes #12", "main.c"),
    Commit("2014-01-05T23:00:00+01:00", "Carol", "Update docs", "doc/guide.md"),
    Commit("2015-12-24T08:00:00+01:00", "Alice", "Cleanup, resolves #56", "Makefile", "v2.0"),
)

# commit created on a side branch, then merged into the main branch
BRANCH_COMMIT = Commit("2016-02-10T12:00:00+01:00", "Dave", "Add script", "extra.py")
MERGE_COMMIT = Commit("2016-02-11T13:00:00+01:00", "Alice", "Merge branch 'feature'", "")

# tags of the test repository, in chronological order
TAGS = ("v0.1", "v1.0", "v2.0")


def _git_env(home: Path, commit: Commit | None = None) -> dict[str, str]:
    """Return the environment used to run git, ignoring the user configuration."""
    author = commit.author if commit else "Test"
    date = commit.date if commit else "2013-01-01T00:00:00+00:00"
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env.update(
        {
            "HOME": str(home),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(home / "gitconfig"),
            "GIT_AUTHOR_NAME": author,
            "GIT_AUTHOR_EMAIL": f"{author.lower()}@example.com",
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_NAME": author,
            "GIT_COMMITTER_EMAIL": f"{author.lower()}@example.com",
            "GIT_COMMITTER_DATE": date,
            "LC_ALL": "C",
            "TZ": "UTC",
        },
    )
    return env


def _git(repo: Path, args: list[str], home: Path, commit: Commit | None = None) -> None:
    """Run a git command in the test repository."""
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        env=_git_env(home, commit),
        capture_output=True,
        check=True,
        text=True,
    )


def _git_commit(repo: Path, commit: Commit, home: Path) -> None:
    """Create a file (or update it) and commit it in the test repository."""
    path = repo / commit.path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{commit.subject}\n", encoding="utf-8")
    _git(repo, ["add", "--all"], home)
    _git(repo, ["commit", "--quiet", "-m", commit.subject], home, commit)
    if commit.tag:
        _git(repo, ["tag", commit.tag], home, commit)


@pytest.fixture(scope="session")
def git_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a git repository with deterministic commits, authors, dates and tags."""
    base = tmp_path_factory.mktemp("gitchart")
    home = base / "home"
    home.mkdir()
    (home / "gitconfig").write_text("", encoding="utf-8")
    repo = base / "repo"
    repo.mkdir()
    _git(repo, ["-c", "init.defaultBranch=main", "init", "--quiet"], home)
    for commit in COMMITS:
        _git_commit(repo, commit, home)
    _git(repo, ["checkout", "--quiet", "-b", "feature"], home)
    _git_commit(repo, BRANCH_COMMIT, home)
    _git(repo, ["checkout", "--quiet", "main"], home)
    _git(
        repo,
        ["merge", "--quiet", "--no-ff", "--no-edit", "-m", MERGE_COMMIT.subject, "feature"],
        home,
        MERGE_COMMIT,
    )
    return repo


@pytest.fixture
def empty_git_repo(tmp_path: Path) -> Path:
    """Build a git repository without any commit."""
    home = tmp_path / "home"
    home.mkdir()
    (home / "gitconfig").write_text("", encoding="utf-8")
    repo = tmp_path / "empty_repo"
    repo.mkdir()
    _git(repo, ["-c", "init.defaultBranch=main", "init", "--quiet"], home)
    return repo


@pytest.fixture
def rendered(monkeypatch: pytest.MonkeyPatch) -> list[pygal.Graph]:
    """Capture the charts instead of rendering them, and return the captured charts."""
    charts: list[pygal.Graph] = []

    def _capture(_self: GitChart, chart: pygal.Graph) -> None:
        charts.append(chart)

    monkeypatch.setattr(GitChart, "_render", _capture)
    return charts


@pytest.fixture
def make_chart(git_repo: Path) -> Callable[..., GitChart]:
    """Return a factory building a GitChart object on the test repository."""

    def _make_chart(chart_name: str, **kwargs: Any) -> GitChart:  # noqa: ANN401
        kwargs.setdefault("repository", str(git_repo))
        kwargs.setdefault("output", "-")
        return GitChart(chart_name, **kwargs)

    return _make_chart


@pytest.fixture
def build_chart(
    make_chart: Callable[..., GitChart],
    rendered: list[pygal.Graph],
) -> Callable[..., pygal.Graph]:
    """Return a function generating a chart and returning the Pygal chart built."""

    def _build_chart(chart_name: str, **kwargs: Any) -> pygal.Graph:  # noqa: ANN401
        chart = make_chart(chart_name, **kwargs)
        assert chart.generate() is True
        assert len(rendered) == 1
        return rendered[0]

    return _build_chart


@pytest.fixture
def run_gitchart(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Iterator[Callable[..., object]]:
    """Return a function running the command line interface, and returning the exit code.

    The data received on standard input is the string given in the "stdin"
    argument, or nothing at all if this argument is None.
    """
    streams = []
    write_fds = []

    def _open_stdin(stdin: str | None) -> IO[str]:
        if stdin is None:
            # empty pipe: nothing to read on standard input (like in a terminal)
            read_fd, write_fd = os.pipe()
            write_fds.append(write_fd)
            return os.fdopen(read_fd, encoding="utf-8")
        # a real file is always ready to be read with select() and it has a
        # file descriptor (unlike the standard input replaced by pytest)
        path = tmp_path / f"stdin-{len(streams)}.txt"
        path.write_text(stdin, encoding="utf-8")
        return path.open(encoding="utf-8")

    def _run_gitchart(*args: str, stdin: str | None = "") -> object:
        monkeypatch.setattr(sys, "argv", ["gitchart", *args])
        stream = _open_stdin(stdin)
        streams.append(stream)
        monkeypatch.setattr(sys, "stdin", stream)
        with pytest.raises(SystemExit) as exc_info:
            main()
        return exc_info.value.code

    yield _run_gitchart

    for stream in streams:
        stream.close()
    for write_fd in write_fds:
        os.close(write_fd)
