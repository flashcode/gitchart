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

"""Tests on the GitChart class: options, git commands, bar charts, rendering."""

from pathlib import Path
from typing import Any

import pygal
import pytest

from gitchart.gitchart import (
    CHARTS,
    GITCHART_DARK_STYLE,
    GITCHART_LIGHT_STYLE,
    PYGAL_STYLES,
    GitChart,
)
from tests.helpers import FakeChart, FakeGit, bar_data, bar_values

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


# ---------------------------------------------------------------- constructor


def test_init_defaults() -> None:
    """Test the default options of a chart."""
    chart = GitChart("commits_year")
    assert chart.chart_name == "commits_year"
    assert chart.title == "Commits by year"
    assert chart.repository == "."
    assert chart.git_log_options == ["--all"]
    assert chart.output is None
    assert chart.max_diff == 20
    assert chart.sort_max == 0
    assert chart.issues_regex == ""
    assert chart.javascript == [""]
    assert chart.style is GITCHART_LIGHT_STYLE
    assert chart.in_data is None
    assert chart.weekdays == WEEKDAYS
    assert chart.months == MONTHS


def test_init_options() -> None:
    """Test the options of a chart."""
    chart = GitChart(
        "authors",
        title="Contributors",
        repository="/path/to/repo",
        no_merges=True,
        output="authors.svg",
        max_diff=5,
        sort_max=-3,
        issues_regex="#([0-9]+)",
        js_files="one.js,two.js",
        style="gitchart_dark",
        in_data="v1.0\n",
    )
    assert chart.title == "Contributors"
    assert chart.repository == "/path/to/repo"
    assert chart.git_log_options == ["--all", "--no-merges"]
    assert chart.output == "authors.svg"
    assert chart.max_diff == 5
    assert chart.sort_max == -3
    assert chart.issues_regex == "#([0-9]+)"
    assert chart.javascript == ["one.js", "two.js"]
    assert chart.style is GITCHART_DARK_STYLE
    assert chart.in_data == "v1.0\n"


@pytest.mark.parametrize("chart_name", sorted(CHARTS))
def test_init_default_title(chart_name: str) -> None:
    """Test the default title of each chart."""
    assert GitChart(chart_name).title == CHARTS[chart_name]


def test_init_unknown_chart() -> None:
    """Test the creation of a chart with an unknown name."""
    with pytest.raises(KeyError):
        GitChart("unknown")
    # with an explicit title, the name of chart is not checked in constructor
    assert GitChart("unknown", title="Unknown").title == "Unknown"


def test_init_unknown_style() -> None:
    """Test the creation of a chart with an unknown style."""
    with pytest.raises(KeyError):
        GitChart("authors", style="unknown")


@pytest.mark.parametrize("style", sorted(PYGAL_STYLES))
def test_init_styles(style: str) -> None:
    """Test the creation of a chart with each supported style."""
    assert GitChart("authors", style=style).style is PYGAL_STYLES[style]


# --------------------------------------------------------------- git commands


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (None, ["git", "log", "--all"]),
        ("", ["git", "log", "--all"]),
        ("--pretty=short", ["git", "log", "--all", "--pretty=short"]),
        (
            ["--date=iso", "--pretty=format:%ad"],
            ["git", "log", "--all", "--date=iso", "--pretty=format:%ad"],
        ),
        (("--date=rfc",), ["git", "log", "--all", "--date=rfc"]),
    ],
)
def test_git_command_log_arguments(
    arguments: tuple[str] | list[str] | str | None,
    expected: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the git log command built with extra arguments."""
    chart = GitChart("authors")
    fake_git = FakeGit("output line")
    monkeypatch.setattr(chart, "_git_command", fake_git)
    assert chart._git_command_log(arguments) == ["output line"]
    assert fake_git.calls == [(expected, None)]


def test_git_command_log_second_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the git log command built with a second piped command."""
    chart = GitChart("authors")
    fake_git = FakeGit()
    monkeypatch.setattr(chart, "_git_command", fake_git)
    chart._git_command_log("--pretty=short", ["git", "shortlog", "-sn"])
    assert fake_git.calls == [
        (["git", "log", "--all", "--pretty=short"], ["git", "shortlog", "-sn"]),
    ]


def test_git_command_log_no_merges(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the git log command built without merge commits."""
    chart = GitChart("authors", no_merges=True)
    fake_git = FakeGit()
    monkeypatch.setattr(chart, "_git_command", fake_git)
    chart._git_command_log("--pretty=format:%ad")
    assert fake_git.calls == [
        (["git", "log", "--all", "--no-merges", "--pretty=format:%ad"], None),
    ]


def test_git_command(git_repo: Path) -> None:
    """Test the execution of a single git command."""
    chart = GitChart("authors", repository=str(git_repo))
    assert chart._git_command(["git", "rev-list", "--count", "--all"]) == ["8"]


def test_git_command_piped(git_repo: Path) -> None:
    """Test the execution of two piped git commands."""
    chart = GitChart("authors", repository=str(git_repo))
    stdout = chart._git_command(
        ["git", "log", "--all", "--pretty=short"],
        ["git", "shortlog", "-sn"],
    )
    authors = dict(line.strip().split("\t", 1)[::-1] for line in stdout)
    assert authors == {"Alice": "4", "Bob": "2", "Carol": "1", "Dave": "1"}


def test_git_command_without_commits(empty_git_repo: Path) -> None:
    """Test the execution of a git command in a repository without commits."""
    chart = GitChart("authors", repository=str(empty_git_repo))
    assert chart._git_command(["git", "log", "--all", "--pretty=format:%ad"]) == [""]


# ------------------------------------------------------------------ bar chart


def test_bar_chart(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart: keys are sorted, title and options are set."""
    chart = GitChart("commits_year", title="Commits", js_files="one.js")
    chart._generate_bar_chart({"2015": 3, "2013": 1, "2014": 2})
    assert len(rendered) == 1
    assert rendered[0].title == "Commits"
    assert rendered[0].config.js == ["one.js"]
    assert rendered[0].config.show_legend is False
    assert rendered[0].config.x_label_rotation == 0
    assert bar_data(rendered[0]) == {"2013": 1, "2014": 2, "2015": 3}


def test_bar_chart_sorted_keys(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart with an explicit order of keys."""
    chart = GitChart("commits_day_week")
    chart._generate_bar_chart({"Tue": 2, "Mon": 1}, sorted_keys=["Tue", "Mon"])
    assert list(rendered[0].x_labels) == ["Tue", "Mon"]
    assert bar_values(rendered[0]) == [2, 1]


def test_bar_chart_x_label_rotation(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart with rotated x labels."""
    chart = GitChart("commits_day")
    chart._generate_bar_chart({"2013-03-15": 1}, x_label_rotation=45)
    assert rendered[0].config.x_label_rotation == 45


def test_bar_chart_sort_max(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart keeping only the entries with the highest values."""
    chart = GitChart("commits_year", sort_max=2)
    chart._generate_bar_chart({"2013": 1, "2014": 5, "2015": 3})
    # the two highest values, sorted by ascending value
    assert list(rendered[0].x_labels) == ["2015", "2014"]
    assert bar_values(rendered[0]) == [3, 5]


def test_bar_chart_sort_max_reverse(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart keeping the entries with the highest values, reversed."""
    chart = GitChart("commits_year", sort_max=-2)
    chart._generate_bar_chart({"2013": 1, "2014": 5, "2015": 3})
    # the two highest values, sorted by descending value
    assert list(rendered[0].x_labels) == ["2014", "2015"]
    assert bar_values(rendered[0]) == [5, 3]


def test_bar_chart_max_keys(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart keeping only the last keys."""
    chart = GitChart("commits_day")
    data = {f"2013-03-{day:02d}": day for day in range(1, 6)}
    chart._generate_bar_chart(data, max_keys=2)
    assert bar_data(rendered[0]) == {"2013-03-04": 4, "2013-03-05": 5}


def test_bar_chart_max_x_labels(rendered: list[pygal.Graph]) -> None:
    """Test a bar chart with a limited number of x labels."""
    chart = GitChart("commits_year_month")
    data = {f"2013-{month:02d}": month for month in range(1, 11)}
    chart._generate_bar_chart(data, max_x_labels=3)
    # all values are kept, only some labels are hidden: one label is kept
    # every 6 labels, starting from the end
    assert bar_values(rendered[0]) == list(range(1, 11))
    assert list(rendered[0].x_labels) == [
        "", "", "", "2013-04", "", "", "", "", "", "2013-10",
    ]


# ------------------------------------------------------------------ rendering


def test_render_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the rendering of a chart on standard output."""
    chart = GitChart("authors", output="-")
    fake_chart: Any = FakeChart()
    chart._render(fake_chart)
    assert fake_chart.calls == [("render", None)]
    assert "<svg>fake chart</svg>" in capsys.readouterr().out


def test_render_svg(tmp_path: Path) -> None:
    """Test the rendering of a chart in a SVG file."""
    filename = str(tmp_path / "chart.svg")
    chart = GitChart("authors", output=filename)
    fake_chart: Any = FakeChart()
    chart._render(fake_chart)
    assert fake_chart.calls == [("render_to_file", filename)]


@pytest.mark.parametrize("extension", ["png", "PNG"])
def test_render_png(extension: str, tmp_path: Path) -> None:
    """Test the rendering of a chart in a PNG file."""
    filename = str(tmp_path / f"chart.{extension}")
    chart = GitChart("authors", output=filename)
    fake_chart: Any = FakeChart()
    chart._render(fake_chart)
    assert fake_chart.calls == [("render_to_png", filename)]


def test_render_svg_file(git_repo: Path, tmp_path: Path) -> None:
    """Test the generation of a real SVG file with Pygal."""
    path = tmp_path / "authors.svg"
    chart = GitChart("authors", repository=str(git_repo), output=str(path))
    assert chart.generate() is True
    svg = path.read_text(encoding="utf-8")
    assert svg.startswith("<?xml")
    assert "Authors" in svg
    assert "Alice (4)" in svg


# ------------------------------------------------------------------- generate


def test_generate(git_repo: Path, rendered: list[pygal.Graph]) -> None:
    """Test the generation of a chart."""
    chart = GitChart("authors", repository=str(git_repo), output="-")
    assert chart.generate() is True
    assert len(rendered) == 1


def test_generate_unknown_chart(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the generation of a chart with an unknown name."""
    chart = GitChart("unknown", title="Unknown", output="-")
    assert chart.generate() is False
    assert "AttributeError" in capsys.readouterr().err


def test_generate_error(
    empty_git_repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the generation of a chart on a repository without commits."""
    chart = GitChart("authors", repository=str(empty_git_repo), output="-")
    assert chart.generate() is False
    assert "ValueError" in capsys.readouterr().err
