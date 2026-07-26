#
# SPDX-FileCopyrightText: 2013-2026 Sébastien Helleu <flashcode@flashtux.org>
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

"""Command line interface of Gitchart."""

import argparse
import importlib.metadata
import os
import select
import sys

import pygal

from gitchart.gitchart import (
    CHARTS,
    DEFAULT_STYLE,
    ISSUES_REGEX_DEFAULT,
    PYGAL_STYLES,
    GitChart,
)


def main() -> None:
    """Generate statistic charts on Git repository."""
    # parse command line arguments
    pygal_config = pygal.Config()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate statistic charts for a git repository.",
        epilog="Return value: 0 = success, 1 = error.",
    )
    parser.add_argument(
        "-t",
        "--title",
        help="override the default chart title",
    )
    parser.add_argument(
        "-r",
        "--repo",
        default=".",
        help="directory with git repository",
    )
    parser.add_argument(
        "-m",
        "--no-merges",
        action="store_true",
        help=("do not count merge commits in git log commands"),
    )
    parser.add_argument(
        "-d",
        "--max-diff",
        type=int,
        default=20,
        help=(
            "max different entries in chart: after this number, an entry is "
            'counted in "others" (for charts authors and files_type); max '
            "number of days (for charts authors, tickets_author, "
            "commits_day, files_type); 0=unlimited"
        ),
    )
    parser.add_argument(
        "-s",
        "--sort-max",
        type=int,
        default=0,
        help=(
            "keep max entries in chart and sort them by value; a negative "
            "number will reverse the sort (only for charts: "
            "commits_hour_day, commits_day, commits_day_week, "
            "commits_month, commits_year, commits_year_month, "
            "commits_version); 0=no sort/max"
        ),
    )
    parser.add_argument(
        "-i",
        "--issues-regex",
        default=ISSUES_REGEX_DEFAULT,
        help=(
            "regular expression to match issues in subject of commits "
            "(the first group captured is used as the issue number) "
            "(for chart tickets_author)"
        ),
    )
    parser.add_argument(
        "-j",
        "--js",
        default=",".join(pygal_config.js),  # ty: ignore[no-matching-overload]
        help="comma-separated list of javascript files/links used in SVG",
    )
    styles = ", ".join(PYGAL_STYLES.keys())
    parser.add_argument(
        "-S",
        "--style",
        default=DEFAULT_STYLE,
        choices=PYGAL_STYLES.keys(),
        help=f"Pygal style to use, one of: {styles}",
    )
    charts = ", ".join(sorted(CHARTS))
    parser.add_argument(
        "chart",
        metavar="chart",
        choices=sorted(CHARTS),
        help=f"name of chart, one of: {charts}",
    )
    parser.add_argument(
        "output",
        help=(
            'output file (svg or png), special value "-" displays SVG '
            "content on standard output"
        ),
    )
    version = importlib.metadata.version("gitchart")
    parser.add_argument(
        "-v", "--version", action="version", version=version,
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args(sys.argv[1:])

    # check javascript files
    if not args.js:
        sys.exit("ERROR: missing javascript file(s)")

    # read data on standard input
    in_data = ""
    while True:
        inr = select.select([sys.stdin], [], [], 0)[0]
        if not inr:
            break
        data = os.read(sys.stdin.fileno(), 4096)
        if not data:
            break
        in_data += data.decode("utf-8")

    # generate chart
    chart = GitChart(
        args.chart,
        args.title,
        args.repo,
        args.no_merges,
        args.output,
        args.max_diff,
        args.sort_max,
        args.issues_regex,
        args.js,
        args.style,
        in_data,
    )
    if chart.generate():
        sys.exit(0)

    # error
    print("ERROR: failed to generate chart:", vars(args))
    sys.exit(1)
