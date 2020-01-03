#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2020 Sébastien Helleu <flashcode@flashtux.org>
#
# This file is part of gitchart.
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
# along with gitchart.  If not, see <https://www.gnu.org/licenses/>.

"""
Generate statistic charts on Git repositories using pygal (http://pygal.org).

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

from __future__ import division, print_function

import argparse
import datetime
import os
import re
import select
import subprocess
import sys
import traceback

import pygal

VERSION = '1.5-dev'

ISSUES_REGEX_DEFAULT = re.compile(
    r'(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)'
    r' *#([0-9]+)'
)


# pylint: disable=too-few-public-methods,too-many-instance-attributes
class GitChart(object):
    """Generate a git stat chart."""

    charts = {
        'authors': 'Authors',
        'tickets_author': 'Tickets processed by author',
        'commits_hour_day': 'Commits by hour of day',
        'commits_hour_week': 'Commits by hour of week',
        'commits_day': 'Commits by day',
        'commits_day_week': 'Commits by day of week',
        'commits_month': 'Commits by month of year',
        'commits_year': 'Commits by year',
        'commits_year_month': 'Commits by year/month',
        'commits_version': 'Commits by version',
        'files_type': 'Files by extension',
    }
    weekdays = [datetime.date(2001, 1, day).strftime('%a')
                for day in range(1, 8)]
    months = [datetime.date(2001, month, 1).strftime('%b')
              for month in range(1, 13)]
    # Pygal style with transparent background and custom colors
    style = pygal.style.Style(
        background='transparent',
        plot_background='transparent',
        foreground='rgba(0, 0, 0, 0.9)',
        foreground_light='rgba(0, 0, 0, 0.6)',
        foreground_dark='rgba(0, 0, 0, 0.2)',
        opacity_hover='.4',
        colors=('#9999ff', '#8cedff', '#b6e354',
                '#feed6c', '#ff9966', '#ff0000',
                '#ff00cc', '#899ca1', '#bf4646')
    )

    # pylint: disable=too-many-arguments
    def __init__(self, chart_name, title=None, repository='.', no_merges=False,
                 output=None, max_diff=20, sort_max=0, issues_regex='',
                 js='', in_data=None):
        self.chart_name = chart_name
        self.title = title if title is not None else self.charts[chart_name]
        self.repository = repository
        self.git_log_options = ['--all']
        if no_merges:
            self.git_log_options += ['--no-merges']
        self.output = output
        self.max_diff = max_diff
        self.sort_max = sort_max
        self.issues_regex = issues_regex
        self.javascript = js.split(',')
        self.in_data = in_data

    def _git_command(self, command1, command2=None):
        """
        Execute one or two piped git commands.

        Return the output lines as a list.
        """
        if command2:
            # pipe the two commands and return output
            proc1 = subprocess.Popen(command1, stdout=subprocess.PIPE,
                                     cwd=self.repository)
            proc2 = subprocess.Popen(command2, stdin=proc1.stdout,
                                     stdout=subprocess.PIPE,
                                     cwd=self.repository)
            proc1.stdout.close()
            return (proc2.communicate()[0].decode('utf-8', errors='ignore')
                    .strip().split('\n'))

        # execute a single git cmd and return output
        proc = subprocess.Popen(command1, stdout=subprocess.PIPE,
                                cwd=self.repository)
        return (proc.communicate()[0].decode('utf-8', errors='ignore')
                .strip().split('\n'))

    def _git_command_log(self, arguments, command2=None):
        """
        Execute a "git log" command with optional extra arguments and second
        command.
        """
        git_log_cmd = ['git', 'log'] + self.git_log_options
        if arguments:
            if isinstance(arguments, (tuple, list)):
                git_log_cmd += arguments
            else:
                git_log_cmd += [arguments]
        return self._git_command(git_log_cmd, command2)

    # pylint: disable=too-many-arguments
    def _generate_bar_chart(self, data, sorted_keys=None, max_keys=0,
                            max_x_labels=0, x_label_rotation=0):
        """Generate a bar chart."""
        bar_chart = pygal.Bar(style=self.style, show_legend=False,
                              x_label_rotation=x_label_rotation,
                              label_font_size=12, js=self.javascript)
        bar_chart.title = self.title
        # sort and keep max entries (if asked)
        if self.sort_max != 0:
            sorted_keys = sorted(data, key=data.get, reverse=self.sort_max < 0)
            keep = -1 * self.sort_max
            if keep > 0:
                sorted_keys = sorted_keys[:keep]
            else:
                sorted_keys = sorted_keys[keep:]
        elif not sorted_keys:
            sorted_keys = sorted(data)
        if max_keys != 0:
            sorted_keys = sorted_keys[-1 * max_keys:]
        bar_chart.x_labels = sorted_keys[:]
        if len(bar_chart.x_labels) > max_x_labels > 0:
            # reduce number of x labels for readability: keep only one label
            # on N, starting from the end
            num = max(2, (len(bar_chart.x_labels) // max_x_labels) * 2)
            count = 0
            for i in range(len(bar_chart.x_labels) - 1, -1, -1):
                if count % num != 0:
                    bar_chart.x_labels[i] = ''
                count += 1
        bar_chart.add('', [data[k] for k in sorted_keys])
        self._render(bar_chart)

    def _chart_authors(self):
        """Generate pie chart with git authors."""
        # format of lines in stdout:   278  John Doe
        stdout = self._git_command_log('--pretty=short',
                                       ['git', 'shortlog', '-sn'])
        pie_chart = pygal.Pie(style=self.style, truncate_legend=100,
                              value_font_size=12, js=self.javascript)
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        for author in stdout:
            (number, name) = author.strip(' ').split('\t', 1)
            count += 1
            if self.max_diff <= 0 or count <= self.max_diff:
                pie_chart.add(name + ' ({0})'.format(number), int(number))
            else:
                count_others += 1
                sum_others += int(number)
        if count_others:
            pie_chart.add('{0} others ({1})'.format(count_others, sum_others),
                          sum_others)
        self._render(pie_chart)
        return True

    def _chart_tickets_author(self):
        """Generate pie chart with processed tickets, by author."""
        # format of lines in stdout: John Doe,refs #1234: fix something
        stdout = self._git_command_log('--pretty=format:%aN,%s')
        pie_chart = pygal.Pie(style=self.style, truncate_legend=100,
                              value_font_size=12, js=self.javascript)
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        tickets_author = {}
        for commit in stdout:
            author, msg = commit.split(',', 1)
            match = re.search(self.issues_regex, msg)
            if match and match.lastindex:
                tickets_author.setdefault(author, set()).add(match.group(1))
        tickets_author = {
            name: len(tickets)
            for name, tickets in tickets_author.items()
        }
        for name, number in sorted(tickets_author.items(),
                                   key=lambda x: x[1],
                                   reverse=True):
            count += 1
            if self.max_diff <= 0 or count <= self.max_diff:
                pie_chart.add(name + ' ({0})'.format(number), number)
            else:
                count_others += 1
                sum_others += int(number)
        if count_others:
            pie_chart.add('{0} others ({1})'.format(count_others, sum_others),
                          sum_others)
        self._render(pie_chart)
        return True

    def _chart_commits_hour_day(self):
        """Generate bar chart with commits by hour of day."""
        # format of lines in stdout: 2013-03-15 18:27:55 +0100
        stdout = self._git_command_log(['--date=iso', '--pretty=format:%ad'])
        commits = {'{0:02d}'.format(hour): 0 for hour in range(0, 24)}
        for line in stdout:
            commits[line.split()[1].split(':')[0]] += 1
        self._generate_bar_chart(commits)
        return True

    def _chart_commits_hour_week(self):
        """Generate dot chart with commits by hour of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command_log(['--date=rfc', '--pretty=format:%ad'])
        commits = {day: {'{0:02d}'.format(hour): 0 for hour in range(0, 24)}
                   for day in self.weekdays}
        for line in stdout:
            wday, _, _, _, hour, _ = line.split()
            commits[wday[:-1]][hour.split(':')[0]] += 1
        dot_chart = pygal.Dot(style=self.style, js=self.javascript)
        dot_chart.title = self.title
        dot_chart.x_labels = ['{0:02d}'.format(hh) for hh in range(0, 24)]
        for day in self.weekdays:
            dot_chart.add(day, commits[day])
        self._render(dot_chart)
        return True

    def _chart_commits_day(self):
        """Generate bar chart with commits by day."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(['--date=short', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            commits[line] = commits.get(line, 0) + 1
        self._generate_bar_chart(commits, max_keys=self.max_diff,
                                 x_label_rotation=45)
        return True

    def _chart_commits_day_week(self):
        """Generate bar chart with commits by day of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command_log(['--date=rfc', '--pretty=format:%ad'])
        commits = {day: 0 for day in self.weekdays}
        for line in stdout:
            commits[line.split(',')[0]] += 1
        self._generate_bar_chart(commits,
                                 sorted_keys=sorted(commits,
                                                    key=self.weekdays.index))
        return True

    def _chart_commits_month(self):
        """Generate bar chart with commits by month of year."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(['--date=short', '--pretty=format:%ad'])
        commits = {month: 0 for month in self.months}
        for line in stdout:
            month = int(line.split('-')[1]) - 1
            commits[self.months[month]] += 1
        self._generate_bar_chart(commits,
                                 sorted_keys=sorted(commits,
                                                    key=self.months.index))
        return True

    def _chart_commits_year(self):
        """Generate bar chart with commits by year."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(['--date=short', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            year = line.split('-')[0]
            commits[year] = commits.get(year, 0) + 1
        self._generate_bar_chart(commits)
        return True

    def _chart_commits_year_month(self):
        """Generate bar chart with commits by year/month."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command_log(['--date=short', '--pretty=format:%ad'])
        commits = {}
        min_date = 999999
        max_date = 0
        for line in stdout:
            year, month = line.split('-')[0:2]
            date = (int(year) * 100) + int(month)
            min_date = min(min_date, date)
            max_date = max(max_date, date)
            year_month = '{0}-{1}'.format(year, month)
            commits[year_month] = commits.get(year_month, 0) + 1
        if min_date != 999999:
            date = min_date
            while date < max_date:
                year_month = '{0:04d}-{1:02d}'.format(date // 100, date % 100)
                commits[year_month] = commits.get(year_month, 0)
                if date % 100 == 12:
                    # next year, for example: 201312 => 201401 (+89)
                    date += 89
                else:
                    date += 1
        self._generate_bar_chart(commits, max_x_labels=30, x_label_rotation=45)
        return True

    def _chart_commits_version(self):
        """Generate bar chart with commits by version (tag)."""
        if not self.in_data:
            return False
        commits = {}
        oldtag = ''
        for tag in self.in_data.strip().split('\n'):
            # transform version to keep only digits with period as separator,
            # examples:
            #   release-0-0-1  =>  0.0.1
            #   v0.3.0         =>  0.3.0
            tag2 = re.sub('([^0-9]+)', ' ', tag).strip().replace(' ', '.')
            commits[tag2] = len(
                self._git_command(['git', 'log',
                                   oldtag + '..' + tag if oldtag else tag,
                                   '--pretty=oneline']))
            oldtag = tag
        self._generate_bar_chart(commits, x_label_rotation=90)
        return True

    def _chart_files_type(self):
        """Generate pie chart with files by extension."""
        # format of lines in stdout: path/to/file.c
        stdout = self._git_command(['git', 'ls-tree', '-r', '--name-only',
                                    'HEAD'])
        extensions = {}
        for line in stdout:
            ext = os.path.splitext(line)[1]
            if not ext:
                ext = '(no extension)'
            extensions[ext] = extensions.get(ext, 0) + 1
        pie_chart = pygal.Pie(style=self.style, truncate_legend=100,
                              value_font_size=12, js=self.javascript)
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        for ext in sorted(extensions, key=extensions.get, reverse=True):
            count += 1
            if self.max_diff <= 0 or count <= self.max_diff:
                pie_chart.add(ext + ' ({0})'.format(extensions[ext]),
                              extensions[ext])
            else:
                count_others += 1
                sum_others += extensions[ext]
        if count_others:
            pie_chart.add('{0} others ({1})'.format(count_others, sum_others),
                          sum_others)
        self._render(pie_chart)
        return True

    def _render(self, chart):
        """Render the chart in a file (or stdout)."""
        if self.output == '-':
            # display SVG on stdout
            print(chart.render())
        elif self.output.lower().endswith('.png'):
            # write PNG in file
            chart.render_to_png(self.output)
        else:
            # write SVG in file
            chart.render_to_file(self.output)

    def generate(self):
        """Generate a chart, and return True if OK, False if error."""
        try:
            # call method to build chart (name of method is dynamic)
            return getattr(self, '_chart_' + self.chart_name)()
        except Exception:  # pylint: disable=broad-except
            traceback.print_exc()
            return False


def main():
    """Main function, entry point."""
    # parse command line arguments
    pygal_config = pygal.Config()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Generate statistic charts for a git repository.',
        epilog='Return value: 0 = success, 1 = error.')
    parser.add_argument(
        '-t', '--title',
        help='override the default chart title')
    parser.add_argument(
        '-r', '--repo',
        default='.',
        help='directory with git repository')
    parser.add_argument(
        '-m', '--no-merges',
        action='store_true',
        help=('do not count merge commits in git log commands'))
    parser.add_argument(
        '-d', '--max-diff',
        type=int, default=20,
        help=('max different entries in chart: after this number, an entry is '
              'counted in "others" (for charts authors and files_type); max '
              'number of days (for charts authors, tickets_author, '
              'commits_day, files_type); 0=unlimited'))
    parser.add_argument(
        '-s', '--sort-max',
        type=int, default=0,
        help=('keep max entries in chart and sort them by value; a negative '
              'number will reverse the sort (only for charts: '
              'commits_hour_day, commits_day, commits_day_week, '
              'commits_month, commits_year, commits_year_month, '
              'commits_version); 0=no sort/max'))
    parser.add_argument(
        '-i', '--issues-regex',
        default=ISSUES_REGEX_DEFAULT,
        help=('regular expression to match issues in subject of commits '
              '(the first group captured is used as the issue number) '
              '(for chart tickets_author)'))
    parser.add_argument(
        '-j', '--js',
        default=','.join(pygal_config.js),
        help='comma-separated list of javascript files/links used in SVG')
    parser.add_argument(
        'chart',
        metavar='chart', choices=sorted(GitChart.charts),
        help='{0}: {1}'.format('name of chart, one of',
                               ', '.join(sorted(GitChart.charts))))
    parser.add_argument(
        'output',
        help=('output file (svg or png), special value "-" displays SVG '
              'content on standard output'))
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=VERSION)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args(sys.argv[1:])

    # check javascript files
    if not args.js:
        sys.exit('ERROR: missing javascript file(s)')

    # read data on standard input
    in_data = ''
    while True:
        inr = select.select([sys.stdin], [], [], 0)[0]
        if not inr:
            break
        data = os.read(sys.stdin.fileno(), 4096)
        if not data:
            break
        in_data += data.decode('utf-8')

    # generate chart
    chart = GitChart(args.chart, args.title, args.repo, args.no_merges,
                     args.output, args.max_diff, args.sort_max,
                     args.issues_regex, args.js, in_data)
    if chart.generate():
        sys.exit(0)

    # error
    print('ERROR: failed to generate chart:', vars(args))
    sys.exit(1)


if __name__ == "__main__":
    main()
