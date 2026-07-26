#
# SPDX-FileCopyrightText: 2026 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Gitchart.
#
# Gitchart is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Gitchart is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gitchart.  If not, see <https://www.gnu.org/licenses/>.
#

"""Tests on the command line interface."""

import importlib.metadata
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

import gitchart
from tests.conftest import TAGS

ARGPARSE_ERROR = 2


def test_main(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the entry point of the package."""
    monkeypatch.setattr(sys, "argv", ["gitchart"])
    with pytest.raises(SystemExit) as exc_info:
        gitchart.main()
    assert exc_info.value.code == 1
    assert capsys.readouterr().out.startswith("usage: gitchart")


def test_no_arguments(
    run_gitchart: Callable[..., object],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the command without any argument: the help is displayed."""
    assert run_gitchart() == 1
    assert capsys.readouterr().out.startswith("usage: gitchart")


def test_version(
    run_gitchart: Callable[..., object],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the option --version."""
    assert run_gitchart("--version") == 0
    version = importlib.metadata.version("gitchart")
    assert capsys.readouterr().out.strip() == version


def test_help(
    run_gitchart: Callable[..., object],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the option --help: all charts and styles are displayed."""
    assert run_gitchart("--help") == 0
    stdout = capsys.readouterr().out
    assert "commits_year_month" in stdout
    assert "gitchart_dark" in stdout


def test_unknown_chart(run_gitchart: Callable[..., object]) -> None:
    """Test the command with an unknown chart name."""
    assert run_gitchart("unknown", "chart.svg") == ARGPARSE_ERROR


def test_unknown_style(run_gitchart: Callable[..., object]) -> None:
    """Test the command with an unknown style."""
    assert run_gitchart("--style", "unknown", "authors", "chart.svg") == ARGPARSE_ERROR


def test_missing_output(run_gitchart: Callable[..., object]) -> None:
    """Test the command without output file."""
    assert run_gitchart("authors") == ARGPARSE_ERROR


def test_missing_javascript(run_gitchart: Callable[..., object]) -> None:
    """Test the command with an empty list of javascript files."""
    assert run_gitchart("--js", "", "authors", "chart.svg") == (
        "ERROR: missing javascript file(s)"
    )


def test_generate_svg(
    run_gitchart: Callable[..., object],
    git_repo: Path,
    tmp_path: Path,
) -> None:
    """Test the generation of a chart in a SVG file."""
    output = tmp_path / "authors.svg"
    assert run_gitchart("--repo", str(git_repo), "authors", str(output)) == 0
    svg = output.read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "Authors" in svg
    assert "Alice (4)" in svg


def test_generate_svg_options(
    run_gitchart: Callable[..., object],
    git_repo: Path,
    tmp_path: Path,
) -> None:
    """Test the generation of a chart with a custom title, style and javascript."""
    output = tmp_path / "commits_year.svg"
    assert (
        run_gitchart(
            "--title", "Commits on project X",
            "--repo", str(git_repo),
            "--no-merges",
            "--style", "gitchart_dark",
            "--js", "one.js,two.js",
            "commits_year",
            str(output),
        )
        == 0
    )
    svg = output.read_text(encoding="utf-8")
    assert "Commits on project X" in svg
    assert "one.js" in svg
    assert "two.js" in svg


def test_generate_stdout(
    run_gitchart: Callable[..., object],
    git_repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the generation of a chart on standard output."""
    assert run_gitchart("--repo", str(git_repo), "commits_year", "-") == 0
    assert "<svg" in capsys.readouterr().out


def test_generate_with_stdin(
    run_gitchart: Callable[..., object],
    git_repo: Path,
    tmp_path: Path,
) -> None:
    """Test the generation of a chart with data read on standard input."""
    output = tmp_path / "commits_version.svg"
    in_data = "".join(f"{tag}\n" for tag in TAGS)
    assert (
        run_gitchart(
            "--repo", str(git_repo),
            "commits_version",
            str(output),
            stdin=in_data,
        )
        == 0
    )
    svg = output.read_text(encoding="utf-8")
    assert "Commits by version" in svg
    assert "0.1" in svg


def test_generate_without_stdin(
    run_gitchart: Callable[..., object],
    git_repo: Path,
    tmp_path: Path,
) -> None:
    """Test the generation of a chart without any data on standard input."""
    output = tmp_path / "commits_year.svg"
    assert (
        run_gitchart(
            "--repo", str(git_repo),
            "commits_year",
            str(output),
            stdin=None,
        )
        == 0
    )
    assert "Commits by year" in output.read_text(encoding="utf-8")


def test_generate_error(
    run_gitchart: Callable[..., object],
    empty_git_repo: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the generation of a chart on a repository without commits."""
    output = tmp_path / "authors.svg"
    assert run_gitchart("--repo", str(empty_git_repo), "authors", str(output)) == 1
    assert "ERROR: failed to generate chart" in capsys.readouterr().out
    assert not output.exists()
