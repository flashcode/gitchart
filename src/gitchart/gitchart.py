# SPDX-FileCopyrightText: 2013-2026 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Generate statistic charts on Git repositories using pygal (http://pygal.org).

Charts supported:
                      |       |                             | format of data
   name               | chart | description                 | expected (stdin)
   -------------------+-------+-----------------------------+-----------------
   authors            | pie   | git authors                 | -
   tickets_author     | pie   | processed tickets by author | -
   commits_hour_day   | bar   | commits by hour of day      | -
   commits_hour_week  | dot   | commits by hour of week     | -
   commits_day        | bar   | commits by day              | -
   commits_day_week   | bar   | commits by day of week      | -
   commits_month      | bar   | commits by month of year    | -
   commits_year       | bar   | commits by year             | -
   commits_year_month | bar   | commits by year/month       | -
   commits_version    | bar   | commits by tag/version      | git tag
   files_type         | pie   | files by type (extension)   | -
"""

import datetime
import os
import re
import subprocess
import traceback
from typing import Any

import pygal
import pygal.style

ISSUES_REGEX_DEFAULT = re.compile(
    r"(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved) *"
    r"#([0-9]+)",
)

# Pygal style with transparent background and custom colors (dark version)
GITCHART_DARK_STYLE = pygal.style.Style(
    plot_background="transparent",
    background="#1a1a1a",
    foreground="rgba(150, 150, 150, 0.8)",
    foreground_strong="rgba(220, 220, 220, 0.8)",
    foreground_subtle="rgba(100, 100, 100, 0.4)",
    opacity_hover=".4",
    colors=(
        "#4444ff",
        "#8cedff",
        "#b6e354",
        "#feed6c",
        "#ff9966",
        "#ff0000",
        "#ff00cc",
        "#899ca1",
        "#bf4646",
    ),
)

# Pygal style with transparent background and custom colors (light version)
GITCHART_LIGHT_STYLE = pygal.style.Style(
    plot_background="transparent",
    background="transparent",
    foreground="rgba(0, 0, 0, 0.7)",
    foreground_strong="rgba(0, 0, 0, 0.9)",
    foreground_subtle="rgba(0, 0, 0, 0.2)",
    opacity_hover=".4",
    colors=(
        "#4444ff",
        "#8cedff",
        "#b6e354",
        "#feed6c",
        "#ff9966",
        "#ff0000",
        "#ff00cc",
        "#899ca1",
        "#bf4646",
    ),
)

PYGAL_STYLES = {
    "gitchart_dark": GITCHART_DARK_STYLE,
    "gitchart_light": GITCHART_LIGHT_STYLE,
    "default": pygal.style.DefaultStyle,
    "dark": pygal.style.DarkStyle,
    "neon": pygal.style.NeonStyle,
    "dark_solarized": pygal.style.DarkSolarizedStyle,
    "light_solarized": pygal.style.LightSolarizedStyle,
    "light": pygal.style.LightStyle,
    "clean": pygal.style.CleanStyle,
    "red_blue": pygal.style.RedBlueStyle,
    "dark_colorized": pygal.style.DarkColorizedStyle,
    "light_colorized": pygal.style.LightSolarizedStyle,
    "turquoise": pygal.style.TurquoiseStyle,
    "light_green": pygal.style.LightGreenStyle,
    "dark_green": pygal.style.DarkGreenStyle,
    "dark_green_blue": pygal.style.DarkGreenBlueStyle,
    "blue": pygal.style.BlueStyle,
}

DEFAULT_STYLE = "gitchart_light"

CHARTS = {
    "authors": "Authors",
    "tickets_author": "Tickets processed by author",
    "commits_hour_day": "Commits by hour of day",
    "commits_hour_week": "Commits by hour of week",
    "commits_day": "Commits by day",
    "commits_day_week": "Commits by day of week",
    "commits_month": "Commits by month of year",
    "commits_year": "Commits by year",
    "commits_year_month": "Commits by year/month",
    "commits_version": "Commits by version",
    "files_type": "Files by extension",
}


class GitChart:
    """Generate a git stat chart."""

    MAX_DATE = 999999

    def __init__(  # noqa: PLR0913,PLR0917
        self,
        chart_name: str,
        title: str | None = None,
        repository: str = ".",
        no_merges: bool = False,  # noqa: FBT001,FBT002
        output: str | None = None,
        max_diff: int = 20,
        sort_max: int = 0,
        issues_regex: str = "",
        js_files: str = "",
        style: str = DEFAULT_STYLE,
        in_data: str | None = None,
    ) -> None:
        """Initialize gitchart."""
        self.weekdays = [
            datetime.date(2001, 1, day).strftime("%a") for day in range(1, 8)
        ]
        self.months = [
            datetime.date(2001, month, 1).strftime("%b") for month in range(1, 13)
        ]
        self.chart_name = chart_name
        self.title = title if title is not None else CHARTS[chart_name]
        self.repository = repository
        self.git_log_options = ["--all"]
        if no_merges:
            self.git_log_options += ["--no-merges"]
        self.output = output
        self.max_diff = max_diff
        self.sort_max = sort_max
        self.issues_regex = issues_regex
        self.javascript = js_files.split(",")
        self.style = PYGAL_STYLES[style]
        self.in_data = in_data

    def _git_command(self, command1: list[str], command2: list[str] | None = None) -> list[str]:
        """Execute one or two piped git commands.

        Return the output lines as a list.
        """
        if command2:
            # pipe the two commands and return output
            with subprocess.Popen(  # noqa: S603
                command1, stdout=subprocess.PIPE, cwd=self.repository,
            ) as proc1, subprocess.Popen(  # noqa: S603
                command2,
                stdin=proc1.stdout,
                stdout=subprocess.PIPE,
                cwd=self.repository,
            ) as proc2:
                proc1.stdout.close()  # ty: ignore[unresolved-attribute]
                return (
                    proc2.communicate()[0]
                    .decode("utf-8", errors="ignore")
                    .strip()
                    .split("\n")
                )

        # execute a single git command and return output
        with subprocess.Popen(  # noqa: S603
            command1, stdout=subprocess.PIPE, cwd=self.repository,
        ) as proc:
            return (
                proc.communicate()[0]
                .decode("utf-8", errors="ignore")
                .strip()
                .split("\n")
            )

    def _git_command_log(
        self,
        arguments: tuple[str] | list[str] | str | None,
        command2: list[str] | None = None,
    ) -> list[str]:
        """Execute a "git log" command with optional extra arguments and second command."""
        git_log_cmd = ["git", "log", *self.git_log_options]
        if arguments:
            if isinstance(arguments, (tuple, list)):
                git_log_cmd += arguments
            else:
                git_log_cmd += [arguments]
        return self._git_command(git_log_cmd, command2)

    def _generate_bar_chart(
        self,
        data: dict[Any, int],
        sorted_keys: list[Any] | None = None,
        max_keys: int = 0,
        max_x_labels: int = 0,
        x_label_rotation: int = 0,
    ) -> None:
        """Generate a bar chart."""
        bar_chart = pygal.Bar(
            style=self.style,
            show_legend=False,
            x_label_rotation=x_label_rotation,
            label_font_size=12,
            js=self.javascript,
        )
        bar_chart.title = self.title
        # sort and keep max entries (if asked)
        if self.sort_max != 0:
            sorted_keys = sorted(  # ty: ignore[no-matching-overload]
                data, key=data.get, reverse=self.sort_max < 0,
            )
            keep = -1 * self.sort_max
            sorted_keys = sorted_keys[:keep] if keep > 0 else sorted_keys[keep:]
        elif not sorted_keys:
            sorted_keys = sorted(data)
        if max_keys != 0:
            sorted_keys = sorted_keys[-1 * max_keys :]
        bar_chart.x_labels = sorted_keys[:]
        if len(bar_chart.x_labels) > max_x_labels > 0:
            # reduce number of x labels for readability: keep only one label
            # on N, starting from the end
            num = max(2, (len(bar_chart.x_labels) // max_x_labels) * 2)
            count = 0
            for i in range(len(bar_chart.x_labels) - 1, -1, -1):
                if count % num != 0:
                    bar_chart.x_labels[i] = ""
                count += 1
        bar_chart.add("", [data[k] for k in sorted_keys])
        self._render(bar_chart)

    def _chart_authors(self) -> bool:
        """Generate pie chart with git authors."""
        # format of lines in stdout:   278  John Doe
        stdout = self._git_command_log(
            "--pretty=short", ["git", "shortlog", "-sn"],
        )
        pie_chart = pygal.Pie(
            style=self.style,
            truncate_legend=100,
            value_font_size=12,
            js=self.javascript,
        )
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        for author in stdout:
            (number, name) = author.strip(" ").split("\t", 1)
            count += 1
            if self.max_diff <= 0 or count <= self.max_diff:
                pie_chart.add(name + f" ({number})", int(number))
            else:
                count_others += 1
                sum_others += int(number)
        if count_others:
            pie_chart.add(f"{count_others} others ({sum_others})", sum_others)
        self._render(pie_chart)
        return True

    def _chart_tickets_author(self) -> bool:
        """Generate pie chart with processed tickets, by author."""
        # format of lines in stdout: John Doe,refs #1234: fix something
        stdout = self._git_command_log("--pretty=format:%aN,%s")
        pie_chart = pygal.Pie(
            style=self.style,
            truncate_legend=100,
            value_font_size=12,
            js=self.javascript,
        )
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        tickets_author = {}
        for commit in stdout:
            author, msg = commit.split(",", 1)
            match = re.search(self.issues_regex, msg)
            if match and match.lastindex:
                tickets_author.setdefault(author, set()).add(match.group(1))
        tickets_author = {
            name: len(tickets) for name, tickets in tickets_author.items()
        }
        for name, number in sorted(
            tickets_author.items(), key=lambda x: x[1], reverse=True,
        ):
            count += 1
            if self.max_diff <= 0 or count <= self.max_diff:
                pie_chart.add(name + f" ({number})", number)
            else:
                count_others += 1
                sum_others += int(number)
        if count_others:
            pie_chart.add(f"{count_others} others ({sum_others})", sum_others)
        self._render(pie_chart)
        return True

    def _chart_commits_hour_day(self) -> bool:
        """Generate bar chart with commits by hour of day."""
        # format of lines in stdout: 2013-03-15 18:27:55 +0100
        stdout = self._git_command_log(["--date=iso", "--pretty=format:%ad"])
        commits = {f"{hour:02d}": 0 for hour in range(24)}
        for line in stdout:
            commits[line.split()[1].split(":")[0]] += 1
        self._generate_bar_chart(commits)
        return True

    def _chart_commits_hour_week(self) -> bool:
        """Generate dot chart with commits by hour of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command_log(["--date=rfc", "--pretty=format:%ad"])
        commits = {
            day: {f"{hour:02d}": 0 for hour in range(24)}
            for day in self.weekdays
        }
        for line in stdout:
            wday, _, _, _, hour, _ = line.split()
            commits[wday[:-1]][hour.split(":")[0]] += 1
        dot_chart = pygal.Dot(style=self.style, js=self.javascript)
        dot_chart.title = self.title
        dot_chart.x_labels = [f"{hh:02d}" for hh in range(24)]
        for day in self.weekdays:
            dot_chart.add(day, commits[day])
        self._render(dot_chart)
        return True

    def _chart_commits_day(self) -> bool:
        """Generate bar chart with commits by day."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(
            ["--date=short", "--pretty=format:%ad"],
        )
        commits = {}
        for line in stdout:
            commits[line] = commits.get(line, 0) + 1
        self._generate_bar_chart(
            commits, max_keys=self.max_diff, x_label_rotation=45,
        )
        return True

    def _chart_commits_day_week(self) -> bool:
        """Generate bar chart with commits by day of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command_log(["--date=rfc", "--pretty=format:%ad"])
        commits = dict.fromkeys(self.weekdays, 0)
        for line in stdout:
            commits[line.split(",")[0]] += 1
        self._generate_bar_chart(
            commits, sorted_keys=sorted(commits, key=self.weekdays.index),
        )
        return True

    def _chart_commits_month(self) -> bool:
        """Generate bar chart with commits by month of year."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(
            ["--date=short", "--pretty=format:%ad"],
        )
        commits = dict.fromkeys(self.months, 0)
        for line in stdout:
            month = int(line.split("-")[1]) - 1
            commits[self.months[month]] += 1
        self._generate_bar_chart(
            commits, sorted_keys=sorted(commits, key=self.months.index),
        )
        return True

    def _chart_commits_year(self) -> bool:
        """Generate bar chart with commits by year."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(
            ["--date=short", "--pretty=format:%ad"],
        )
        commits = {}
        for line in stdout:
            year = line.split("-")[0]
            commits[year] = commits.get(year, 0) + 1
        self._generate_bar_chart(commits)
        return True

    def _chart_commits_year_month(self) -> bool:
        """Generate bar chart with commits by year/month."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(
            ["--date=short", "--pretty=format:%ad"],
        )
        commits = {}
        min_date = self.MAX_DATE
        max_date = 0
        for line in stdout:
            year, month = line.split("-")[0:2]
            date = (int(year) * 100) + int(month)
            min_date = min(min_date, date)
            max_date = max(max_date, date)
            year_month = f"{year}-{month}"
            commits[year_month] = commits.get(year_month, 0) + 1
        if min_date != self.MAX_DATE:
            date = min_date
            while date < max_date:
                year_month = f"{date // 100:04d}-{date % 100:02d}"
                commits[year_month] = commits.get(year_month, 0)
                if date % 100 == 12:  # noqa: PLR2004
                    # next year, for example: 201312 => 201401 (+89)
                    date += 89
                else:
                    date += 1
        self._generate_bar_chart(
            commits, max_x_labels=30, x_label_rotation=45,
        )
        return True

    def _chart_commits_version(self) -> bool:
        """Generate bar chart with commits by version (tag)."""
        if not self.in_data:
            return False
        commits = {}
        oldtag = ""
        for tag in self.in_data.strip().split("\n"):
            # transform version to keep only digits with period as separator,
            # examples:
            #   release-0-0-1  =>  0.0.1
            #   v0.3.0         =>  0.3.0
            tag2 = re.sub("([^0-9]+)", " ", tag).strip().replace(" ", ".")
            commits[tag2] = len(
                self._git_command(
                    [
                        "git",
                        "log",
                        oldtag + ".." + tag if oldtag else tag,
                        "--pretty=oneline",
                    ],
                ),
            )
            oldtag = tag
        self._generate_bar_chart(commits, x_label_rotation=90)
        return True

    def _chart_files_type(self) -> bool:
        """Generate pie chart with files by extension."""
        # format of lines in stdout: path/to/file.c
        stdout = self._git_command(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        )
        extensions = {}
        for line in stdout:
            ext = os.path.splitext(line)[1]
            if not ext:
                ext = "(no extension)"
            extensions[ext] = extensions.get(ext, 0) + 1
        pie_chart = pygal.Pie(
            style=self.style,
            truncate_legend=100,
            value_font_size=12,
            js=self.javascript,
        )
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        for ext in sorted(extensions, key=extensions.get, reverse=True):  # ty: ignore[no-matching-overload]
            count += 1
            if self.max_diff <= 0 or count <= self.max_diff:
                pie_chart.add(ext + f" ({extensions[ext]})", extensions[ext])
            else:
                count_others += 1
                sum_others += extensions[ext]
        if count_others:
            pie_chart.add(f"{count_others} others ({sum_others})", sum_others)
        self._render(pie_chart)
        return True

    def _render(self, chart: pygal.Graph) -> None:
        """Render the chart in a file (or stdout)."""
        if self.output == "-":
            # display SVG on stdout
            print(chart.render())
        elif self.output.lower().endswith(".png"):  # ty: ignore[unresolved-attribute]
            # write PNG in file
            chart.render_to_png(self.output)
        else:
            # write SVG in file
            chart.render_to_file(self.output)

    def generate(self) -> bool:
        """Generate a chart, and return True if OK, False if error."""
        try:
            # call method to build chart (name of method is dynamic)
            return getattr(self, "_chart_" + self.chart_name)()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return False

