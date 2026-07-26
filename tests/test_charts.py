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

"""Tests on the data of each chart, built on the test git repository."""

from collections.abc import Callable

import pygal
import pytest

from gitchart.gitchart import CHARTS, ISSUES_REGEX_DEFAULT, GitChart
from tests.conftest import TAGS
from tests.helpers import FakeGit, bar_data, bar_values, dot_data, pie_data

# tags of the test repository, as they are received on standard input
IN_DATA_TAGS = "".join(f"{tag}\n" for tag in TAGS)

# number of commits in the test repository (including the merge commit)
NUM_COMMITS = 8


@pytest.mark.parametrize("chart_name", sorted(CHARTS))
def test_all_charts(chart_name: str, build_chart: Callable[..., pygal.Graph]) -> None:
    """Test that each chart can be built with data and the default title."""
    chart = build_chart(
        chart_name,
        issues_regex=ISSUES_REGEX_DEFAULT,
        in_data=IN_DATA_TAGS,
    )
    assert chart.title == CHARTS[chart_name]
    assert chart.raw_series


@pytest.mark.parametrize("chart_name", sorted(CHARTS))
def test_all_charts_title(chart_name: str, build_chart: Callable[..., pygal.Graph]) -> None:
    """Test that the title of each chart can be customized."""
    chart = build_chart(chart_name, title="My chart", in_data=IN_DATA_TAGS)
    assert chart.title == "My chart"


# -------------------------------------------------------------------- authors


def test_chart_authors(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with authors."""
    chart = build_chart("authors")
    assert pie_data(chart) == {
        "Alice (4)": 4,
        "Bob (2)": 2,
        "Carol (1)": 1,
        "Dave (1)": 1,
    }


def test_chart_authors_no_merges(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with authors, without the merge commits."""
    chart = build_chart("authors", no_merges=True)
    assert pie_data(chart) == {
        "Alice (3)": 3,
        "Bob (2)": 2,
        "Carol (1)": 1,
        "Dave (1)": 1,
    }


def test_chart_authors_max_diff(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with authors, with authors grouped in "others"."""
    chart = build_chart("authors", max_diff=2)
    assert pie_data(chart) == {
        "Alice (4)": 4,
        "Bob (2)": 2,
        "2 others (2)": 2,
    }


def test_chart_authors_max_diff_unlimited(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with authors, without any limit of authors."""
    chart = build_chart("authors", max_diff=0)
    assert len(pie_data(chart)) == 4
    assert sum(pie_data(chart).values()) == NUM_COMMITS


# ------------------------------------------------------------- tickets_author


def test_chart_tickets_author(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with tickets processed by author."""
    chart = build_chart("tickets_author", issues_regex=ISSUES_REGEX_DEFAULT)
    # Alice closed tickets 12 and 56, Bob closed tickets 34 and 12
    assert pie_data(chart) == {"Alice (2)": 2, "Bob (2)": 2}


def test_chart_tickets_author_custom_regex(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with tickets processed by author, with a custom regex."""
    chart = build_chart("tickets_author", issues_regex=r"fixes #([0-9]+)")
    assert pie_data(chart) == {"Alice (1)": 1, "Bob (1)": 1}


def test_chart_tickets_author_no_regex(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with tickets processed by author, without regex."""
    chart = build_chart("tickets_author")
    assert pie_data(chart) == {}


def test_chart_tickets_author_max_diff(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with tickets, with authors grouped in "others"."""
    chart = build_chart(
        "tickets_author",
        issues_regex=ISSUES_REGEX_DEFAULT,
        max_diff=1,
    )
    data = pie_data(chart)
    assert len(data) == 2
    assert data["1 others (2)"] == 2


# ---------------------------------------------------------- commits_hour_day


def test_chart_commits_hour_day(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by hour of day."""
    chart = build_chart("commits_hour_day")
    data = bar_data(chart)
    assert len(data) == 24
    assert sum(data.values()) == NUM_COMMITS
    assert {hour: count for hour, count in data.items() if count} == {
        "08": 1,
        "09": 1,
        "12": 1,
        "13": 1,
        "14": 1,
        "18": 1,
        "22": 1,
        "23": 1,
    }


# ---------------------------------------------------------- commits_hour_week


def test_chart_commits_hour_week(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the dot chart with commits by hour of week."""
    chart = build_chart("commits_hour_week")
    data = dot_data(chart)
    assert list(data) == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    assert list(chart.x_labels) == [f"{hour:02d}" for hour in range(24)]
    commits = {
        (day, hour)
        for day, hours in data.items()
        for hour, count in hours.items()
        if count
    }
    assert commits == {
        ("Tue", "14"),
        ("Wed", "12"),
        ("Thu", "08"),
        ("Thu", "13"),
        ("Fri", "18"),
        ("Sat", "09"),
        ("Sun", "22"),
        ("Sun", "23"),
    }


# --------------------------------------------------------------- commits_day


def test_chart_commits_day(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by day."""
    chart = build_chart("commits_day")
    assert bar_data(chart) == {
        "2013-03-15": 1,
        "2013-03-16": 1,
        "2013-04-02": 1,
        "2014-01-05": 2,
        "2015-12-24": 1,
        "2016-02-10": 1,
        "2016-02-11": 1,
    }
    assert chart.config.x_label_rotation == 45


def test_chart_commits_day_max_diff(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by day, with a max number of days."""
    chart = build_chart("commits_day", max_diff=2)
    assert bar_data(chart) == {"2016-02-10": 1, "2016-02-11": 1}


# ----------------------------------------------------------- commits_day_week


def test_chart_commits_day_week(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by day of week."""
    chart = build_chart("commits_day_week")
    assert bar_data(chart) == {
        "Mon": 0,
        "Tue": 1,
        "Wed": 1,
        "Thu": 2,
        "Fri": 1,
        "Sat": 1,
        "Sun": 2,
    }


# -------------------------------------------------------------- commits_month


def test_chart_commits_month(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by month of year."""
    chart = build_chart("commits_month")
    assert bar_data(chart) == {
        "Jan": 2,
        "Feb": 2,
        "Mar": 2,
        "Apr": 1,
        "May": 0,
        "Jun": 0,
        "Jul": 0,
        "Aug": 0,
        "Sep": 0,
        "Oct": 0,
        "Nov": 0,
        "Dec": 1,
    }


# --------------------------------------------------------------- commits_year


def test_chart_commits_year(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by year."""
    chart = build_chart("commits_year")
    assert bar_data(chart) == {"2013": 3, "2014": 2, "2015": 1, "2016": 2}


# --------------------------------------------------------- commits_year_month


def test_chart_commits_year_month(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by year/month."""
    # months without commits are added, from the first to the last commit
    # (2013-03 to 2016-02, ie 36 months)
    all_months = [
        f"{year}-{month:02d}" for year in range(2013, 2017) for month in range(1, 13)
    ][2:-10]
    commits = {"2013-03": 2, "2013-04": 1, "2014-01": 2, "2015-12": 1, "2016-02": 2}
    chart = build_chart("commits_year_month")
    assert len(all_months) == 36
    assert bar_values(chart) == [commits.get(month, 0) for month in all_months]
    # only one label on two is kept for readability (36 labels > 30)
    labels = list(chart.x_labels)
    assert labels[-1] == "2016-02"
    assert labels[1] == "2013-04"
    assert labels.count("") == 18
    assert chart.config.x_label_rotation == 45


# ------------------------------------------------------------ commits_version


def test_chart_commits_version(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the bar chart with commits by version."""
    chart = build_chart("commits_version", in_data=IN_DATA_TAGS)
    # version names are converted to keep only digits: "v0.1" -> "0.1"
    assert bar_data(chart) == {"0.1": 2, "1.0": 1, "2.0": 3}
    assert chart.config.x_label_rotation == 90


def test_chart_commits_version_other_tag_names(
    rendered: list[pygal.Graph],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the conversion of tag names in the bar chart with commits by version."""
    chart = GitChart("commits_version", output="-", in_data="release-0-0-1\nv0.3.0\n")
    fake_git = FakeGit("commit 1", "commit 2")
    monkeypatch.setattr(chart, "_git_command", fake_git)
    assert chart.generate() is True
    # only digits are kept in tag names, and commits are counted between tags
    assert bar_data(rendered[0]) == {"0.0.1": 2, "0.3.0": 2}
    assert [call[0][2] for call in fake_git.calls] == [
        "release-0-0-1",
        "release-0-0-1..v0.3.0",
    ]


def test_chart_commits_version_without_data(
    make_chart: Callable[..., GitChart],
    rendered: list[pygal.Graph],
) -> None:
    """Test the bar chart with commits by version, without data on standard input."""
    chart = make_chart("commits_version")
    assert chart.generate() is False
    assert rendered == []


# ----------------------------------------------------------------- files_type


def test_chart_files_type(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with files by extension."""
    chart = build_chart("files_type")
    assert pie_data(chart) == {
        ".c (2)": 2,
        ".md (2)": 2,
        ".py (1)": 1,
        "(no extension) (1)": 1,
    }


def test_chart_files_type_max_diff(build_chart: Callable[..., pygal.Graph]) -> None:
    """Test the pie chart with files by extension, with extensions in "others"."""
    chart = build_chart("files_type", max_diff=2)
    data = pie_data(chart)
    assert len(data) == 3
    assert data["2 others (2)"] == 2
