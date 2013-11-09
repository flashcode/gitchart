#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Sebastien Helleu <flashcode@flashtux.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
# Generate statistic charts for a git repository using pygal
# (http://pygal.org).
#
# Charts supported:
#                      |       |                           | format of data
#   name               | chart | description               | expected (stdin)
#   -------------------+-------+---------------------------+-----------------
#   authors            | pie   | git authors               | -
#   commits_hour       | bar   | commits by hour of day    | -
#   commits_hour_week  | dot   | commits by hour of week   | -
#   commits_day        | bar   | commits by day of week    | -
#   commits_month      | bar   | commits by month of year  | -
#   commits_year       | bar   | commits by year           | -
#   commits_year_month | bar   | commits by year/month     | -
#   commits_version    | bar   | commits by tag/version    | git tag
#   files_type         | pie   | files by type (extension) | -
#

from __future__ import division, print_function

import argparse
import datetime
import os
import pygal
import re
import select
import subprocess
import sys
import traceback

VERSION = '0.7'


class GitChart:
    """Generate a git stat chart."""

    charts = {
        'authors': 'Authors',
        'commits_hour': 'Commits by hour of day',
        'commits_hour_week': 'Commits by hour of week',
        'commits_day': 'Commits by day of week',
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
    style = pygal.style.Style(background='transparent',
                              plot_background='transparent',
                              foreground='rgba(0, 0, 0, 0.9)',
                              foreground_light='rgba(0, 0, 0, 0.6)',
                              foreground_dark='rgba(0, 0, 0, 0.2)',
                              opacity_hover='.4',
                              colors=('#9999ff', '#8cedff', '#b6e354',
                                      '#feed6c', '#ff9966', '#ff0000',
                                      '#ff00cc', '#899ca1', '#bf4646'))

    def __init__(self, chart_name, title=None, repository='.', output=None,
                 max_entries=20, in_data=None):
        self.chart_name = chart_name
        self.title = title if title is not None else self.charts[chart_name]
        self.repository = repository
        self.output = output
        self.max_entries = max_entries
        self.in_data = in_data

    def _git_command(self, command1, command2=None):
        """
        Execute one or two piped git commands.
        Return the output lines as a list.
        """
        if command2:
            # pipe the two commands and return output
            p1 = subprocess.Popen(command1, stdout=subprocess.PIPE,
                                  cwd=self.repository)
            p2 = subprocess.Popen(command2, stdin=p1.stdout,
                                  stdout=subprocess.PIPE)
            p1.stdout.close()
            return p2.communicate()[0].decode('utf-8').strip().split('\n')
        else:
            # execute a single git cmd and return output
            p = subprocess.Popen(command1, stdout=subprocess.PIPE,
                                 cwd=self.repository)
            return p.communicate()[0].decode('utf-8').strip().split('\n')

    def _generate_bar_chart(self, data, sorted_keys=None, x_labels=None,
                            x_label_rotation=0):
        """Generate a bar chart."""
        bar_chart = pygal.Bar(style=self.style, show_legend=False,
                              x_label_rotation=x_label_rotation,
                              label_font_size=12)
        bar_chart.title = self.title
        if not sorted_keys:
            sorted_keys = sorted(data)
        bar_chart.x_labels = x_labels if x_labels else sorted_keys
        bar_chart.add('', [data[n] for n in sorted_keys])
        self._render(bar_chart)

    def _chart_authors(self):
        """Generate pie chart with git authors."""
        # format of lines in stdout:   278  John Doe
        stdout = self._git_command(['git', 'log', '--pretty=short'],
                                   ['git', 'shortlog', '-sn'])
        pie_chart = pygal.Pie(style=self.style, truncate_legend=100,
                              value_font_size=12)
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        for author in stdout:
            (number, name) = author.strip().split('\t', 1)
            count += 1
            if self.max_entries <= 0 or count <= self.max_entries:
                pie_chart.add(name + ' ({0})'.format(number), int(number))
            else:
                count_others += 1
                sum_others += int(number)
        if count_others:
            pie_chart.add('{0} others ({1})'.format(count_others, sum_others),
                          sum_others)
        self._render(pie_chart)
        return True

    def _chart_commits_hour(self):
        """Generate bar chart with commits by hour of day."""
        # format of lines in stdout: 2013-03-15 18:27:55 +0100
        stdout = self._git_command(['git', 'log', '--date=iso',
                                    '--pretty=format:%ad'])
        commits = {'{0:02d}'.format(hour): 0 for hour in range(0, 24)}
        for line in stdout:
            commits[line.split()[1].split(':')[0]] += 1
        self._generate_bar_chart(commits)
        return True

    def _chart_commits_hour_week(self):
        """Generate dot chart with commits by hour of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command(['git', 'log', '--date=rfc',
                                    '--pretty=format:%ad'])
        commits = {day: {'{0:02d}'.format(hour): 0 for hour in range(0, 24)}
                   for day in self.weekdays}
        for line in stdout:
            wday, _, _, _, hour, _ = line.split()
            commits[wday[:-1]][hour.split(':')[0]] += 1
        dot_chart = pygal.Dot(style=self.style)
        dot_chart.title = self.title
        dot_chart.x_labels = ['{0:02d}'.format(hour) for hour in range(0, 24)]
        for day in self.weekdays:
            dot_chart.add(day, commits[day])
        self._render(dot_chart)
        return True

    def _chart_commits_day(self):
        """Generate bar chart with commits by day of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command(['git', 'log', '--date=rfc',
                                    '--pretty=format:%ad'])
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
        stdout = self._git_command(['git', 'log', '--date=short',
                                    '--pretty=format:%ad'])
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
        stdout = self._git_command(['git', 'log', '--date=short',
                                    '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            year = line.split('-')[0]
            commits[year] = commits.get(year, 0) + 1
        self._generate_bar_chart(commits)
        return True

    def _chart_commits_year_month(self):
        """Generate bar chart with commits by year/month."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command(['git', 'log', '--date=short',
                                    '--pretty=format:%ad'])
        commits = {}
        min_date = 999999
        max_date = 0
        for line in stdout:
            (year, month, day) = line.split('-')
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
        x_labels = sorted(commits)
        # if there are more than 20 commits, keep one x label on 10
        # (starting from the end)
        if len(commits) > 20:
            n = 0
            for i in range(len(x_labels) - 1, -1, -1):
                if n % 10 != 0:
                    x_labels[i] = ''
                n += 1
        self._generate_bar_chart(commits, x_labels=x_labels,
                                 x_label_rotation=45)
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
                              value_font_size=12)
        pie_chart.title = self.title
        count = 0
        count_others = 0
        sum_others = 0
        for ext in sorted(extensions, key=extensions.get, reverse=True):
            count += 1
            if self.max_entries <= 0 or count <= self.max_entries:
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
            # call function to build chart (name of function is dynamic)
            return getattr(self, '_chart_' + self.chart_name)()
        except:
            traceback.print_exc()
            return False


def main():
    """Main function, entry point."""
    # parse command line arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Generate statistic charts for a git repository.',
        epilog='Return value: 0 = success, 1 = error.')
    parser.add_argument('-t', '--title',
                        help='override the default chart title')
    parser.add_argument('-r', '--repo', default='.',
                        help='directory with git repository')
    parser.add_argument('-m', '--max', type=int, default=20,
                        help='max different entries in chart: after this '
                        'number, an entry is counted in "others" (only for '
                        'charts "authors" and "files_type"), 0=unlimited')
    parser.add_argument('chart', metavar='chart',
                        choices=sorted(GitChart.charts),
                        help='name of chart, one of: ' +
                        ', '.join(sorted(GitChart.charts)))
    parser.add_argument('output', help='output file (svg or png), special '
                        'value "-" displays SVG content on standard output')
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args(sys.argv[1:])

    # read data on standard input
    in_data = ''
    while True:
        inr, outr, exceptr = select.select([sys.stdin], [], [], 0)
        if not inr:
            break
        data = os.read(sys.stdin.fileno(), 4096)
        if not data:
            break
        in_data += data.decode('utf-8')

    # generate chart
    chart = GitChart(args.chart, args.title, args.repo, args.output, args.max,
                     in_data)
    if chart.generate():
        sys.exit(0)

    # error
    print('ERROR: failed to generate chart:', vars(args))
    sys.exit(1)


if __name__ == "__main__":
    main()
