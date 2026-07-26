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

"""Helpers to read the data added to Pygal charts, and fake objects."""

import pygal


class FakeGit:
    """Replacement for GitChart._git_command, returning canned output."""

    def __init__(self, *lines: str) -> None:
        """Initialize the fake git command with the lines it must return."""
        self.lines = list(lines)
        self.calls: list[tuple[list[str], list[str] | None]] = []

    def __call__(self, command1: list[str], command2: list[str] | None = None) -> list[str]:
        """Record the git command executed and return the canned output."""
        self.calls.append((command1, command2))
        return list(self.lines)


class FakeChart:
    """Replacement for a Pygal chart, recording the calls to render methods."""

    def __init__(self) -> None:
        """Initialize the fake chart."""
        self.calls: list[tuple[str, str | None]] = []

    def render(self) -> bytes:
        """Return the chart as SVG."""
        self.calls.append(("render", None))
        return b"<svg>fake chart</svg>"

    def render_to_file(self, filename: str) -> None:
        """Write the chart as SVG in a file."""
        self.calls.append(("render_to_file", filename))

    def render_to_png(self, filename: str) -> None:
        """Write the chart as PNG in a file."""
        self.calls.append(("render_to_png", filename))


def pie_data(chart: pygal.Graph) -> dict[str, int]:
    """Return the slices of a pie chart, as a dict {legend: value}."""
    return {kwargs["title"]: values[0] for values, kwargs in chart.raw_series}


def dot_data(chart: pygal.Graph) -> dict[str, dict[str, int]]:
    """Return the series of a dot chart, as a dict {legend: {label: value}}."""
    return {kwargs["title"]: values for values, kwargs in chart.raw_series}


def bar_values(chart: pygal.Graph) -> list[int]:
    """Return the values of the single series of a bar chart."""
    return chart.raw_series[0][0]


def bar_data(chart: pygal.Graph) -> dict[str, int]:
    """Return a bar chart as a dict {x label: value}.

    The x labels of the chart must be unique (this is not the case if labels
    have been hidden for readability).
    """
    labels = list(chart.x_labels)
    if len(set(labels)) != len(labels):
        msg = f"x labels are not unique: {labels}"
        raise ValueError(msg)
    return dict(zip(labels, bar_values(chart), strict=True))
