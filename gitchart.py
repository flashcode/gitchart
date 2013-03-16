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
# Generate statistic charts for a git repository using pygal (http://pygal.org).
#
# Syntax:
#      gitchart.py <chart> <title> <repository> <output>
#    or:
#      command | gitchart.py <chart> <title> <repository> <output>
#
#      chart       name of chart (see below)
#      title       title of chart
#      repository  directory with git repository
#      output      output path/filename (SVG file)
#
# Charts supported:
#
#   name               | chart | description               | format of data expected (stdin)
#   -------------------+-------+---------------------------+--------------------------------
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
# 2013-03-15, Sebastien Helleu <flashcode@flashtux.org>:
#     version 0.1: initial release
#

import pygal, os, re, select, subprocess, sys, traceback

VERSION = '0.1'

class GitChart:
    """Generate a git stat chart."""

    def __init__(self):
        self.charts = { 'authors'           : self._chart_authors,
                        'commits_hour'      : self._chart_commits_hour,
                        'commits_hour_week' : self._chart_commits_hour_week,
                        'commits_day'       : self._chart_commits_day,
                        'commits_month'     : self._chart_commits_month,
                        'commits_year'      : self._chart_commits_year,
                        'commits_year_month': self._chart_commits_year_month,
                        'commits_version'   : self._chart_commits_version,
                        'files_type'        : self._chart_files_type,
                        }
        # define a Pygal style with transparent background and custom colors
        self.style = pygal.style.Style(
            background='transparent',
            plot_background='transparent',
            foreground='rgba(0, 0, 0, 0.9)',
            foreground_light='rgba(0, 0, 0, 0.6)',
            foreground_dark='rgba(0, 0, 0, 0.2)',
            opacity_hover='.4',
            colors=('#9999ff', '#8cedff', '#b6e354', '#feed6c', '#ff9966', '#ff0000', '#ff00cc', '#899ca1', '#bf4646'))
        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def _git_command(self, repository, command, command2=None):
        """Execute one or two piped git commands return lines as a list."""
        if command2:
            # pipe the two commands and return output
            p1 = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=repository)
            p2 = subprocess.Popen(command2, stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            return p2.communicate()[0].decode('utf-8').strip().split('\n')
        else:
            # execute a single git command and return output
            p = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=repository)
            return p.communicate()[0].decode('utf-8').strip().split('\n')

    def _generate_bar_chart(self, title, data, output, sorted_keys=None, x_labels=None, x_label_rotation=0):
        """Generate a bar chart."""
        bar_chart = pygal.Bar(style=self.style, show_legend=False, x_label_rotation=x_label_rotation, label_font_size=12)
        bar_chart.title = title
        if not sorted_keys:
            sorted_keys = sorted(data)
        bar_chart.x_labels = x_labels if x_labels else sorted_keys
        bar_chart.add('', [data[n] for n in sorted_keys])
        bar_chart.render_to_file(output)

    def _chart_authors(self, title, repository, output, in_data=None, limit=20):
        """Generate pie chart with git authors."""
        # format of lines in stdout:   278  John Doe
        stdout = self._git_command(repository, ['git', 'log', '--pretty=short'], ['git', 'shortlog', '-sn'])
        pie_chart = pygal.Pie(style=self.style, truncate_legend=100, value_font_size=12)
        pie_chart.title = title or 'Authors'
        count = 0
        count_others = 0
        sum_others = 0
        for author in stdout:
            (number, name) = author.strip().split('\t', 1)
            count += 1
            if limit <= 0 or count <= limit:
                pie_chart.add('%s (%s)' % (name, number), int(number))
            else:
                count_others += 1
                sum_others += int(number)
        if count_others:
            pie_chart.add('%d others (%d)' % (count_others, sum_others), sum_others)
        pie_chart.render_to_file(output)
        return True

    def _chart_commits_hour(self, title, repository, output, in_data=None):
        """Generate bar chart with commits by hour of day."""
        # format of lines in stdout: 2013-03-15 18:27:55 +0100
        stdout = self._git_command(repository, ['git', 'log', '--date=iso', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            hour = line.split()[1].split(':')[0]
            commits[hour] = commits.get(hour, 0) + 1
        # ensure each hour of day has a value (set 0 for hours without commits)
        for i in range(0, 24):
            hour = '%02d' % i
            if not hour in commits:
                commits[hour] = 0
        self._generate_bar_chart(title or 'Commits by hour of day', commits, output)
        return True

    def _chart_commits_hour_week(self, title, repository, output, in_data=None):
        """Generate dot chart with commits by hour of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command(repository, ['git', 'log', '--date=rfc', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            items = line.split()
            day = items[0][:-1]
            hour = items[-2].split(':')[0]
            if not day in commits:
                commits[day] = {}
            commits[day][hour] = commits[day].get(hour, 0) + 1
        dot_chart = pygal.Dot(style=self.style)
        dot_chart.title = title or 'Commits by hour of week'
        dot_chart.x_labels = ['%02d' % hour for hour in range(0, 24)]
        for day in sorted(commits, key=self.days.index):
            # ensure each hour of day has a value (set 0 for hours without commits)
            for i in range(0, 24):
                hour = '%02d' % i
                if not hour in commits[day]:
                    commits[day][hour] = 0
            dot_chart.add(day, commits[day])
        dot_chart.render_to_file(output)
        return True

    def _chart_commits_day(self, title, repository, output, in_data=None):
        """Generate bar chart with commits by day of week."""
        # format of lines in stdout: Fri, 15 Mar 2013 18:27:55 +0100
        stdout = self._git_command(repository, ['git', 'log', '--date=rfc', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            day = line.split(',')[0]
            commits[day] = commits.get(day, 0) + 1
        self._generate_bar_chart(title or 'Commits by day of week', commits, output, sorted_keys=sorted(commits, key=self.days.index))
        return True

    def _chart_commits_month(self, title, repository, output, in_data=None):
        """Generate bar chart with commits by month of year."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command(repository, ['git', 'log', '--date=short', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            month = int(line.split('-')[1])
            commits[month] = commits.get(month, 0) + 1
        # transform month number to name (1 => Jan, 2 => Feb,...)
        commits2 = {}
        for month in commits:
            commits2[self.months[month - 1]] = commits[month]
        self._generate_bar_chart(title or 'Commits by month of year', commits2, output, sorted_keys=sorted(commits2, key=self.months.index))
        return True

    def _chart_commits_year(self, title, repository, output, in_data=None):
        """Generate bar chart with commits by year."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command(repository, ['git', 'log', '--date=short', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            year = line.split('-')[0]
            commits[year] = commits.get(year, 0) + 1
        self._generate_bar_chart(title or 'Commits by year', commits, output)
        return True

    def _chart_commits_year_month(self, title, repository, output, in_data=None):
        """Generate bar chart with commits by year/month."""
        # format of lines in stdout: 2013-03-15
        stdout = self._git_command(repository, ['git', 'log', '--date=short', '--pretty=format:%ad'])
        commits = {}
        for line in stdout:
            month = '-'.join(line.split('-')[0:2])
            commits[month] = commits.get(month, 0) + 1
        x_labels = sorted(commits)
        # if there are more than 20 commits, keep one x label on 10 (starting from the end)
        if len(commits) > 20:
            n = 0
            for i in range(len(x_labels) - 1, -1, -1):
                if n % 10 != 0:
                    x_labels[i] = ''
                n += 1
        self._generate_bar_chart(title or 'Commits by year/month', commits, output, x_labels=x_labels, x_label_rotation=45)
        return True

    def _chart_commits_version(self, title, repository, output, in_data=None):
        """Generate bar chart with commits by version (tag)."""
        if not in_data:
            return False
        commits = {}
        oldtag = ''
        for tag in in_data.strip().split('\n'):
            commits[tag] = len(self._git_command(repository, ['git', 'log', '%s..%s' % (oldtag, tag) if oldtag else tag, '--pretty=oneline']))
            oldtag = tag
        # transform version to keep only digits with period as separator, examples:
        #   release-0-0-1  =>  0.0.1
        #   v0.3.0         =>  0.3.0
        commits2 = {}
        for tag in commits:
            commits2[re.sub('([^0-9]+)', ' ', tag).strip().replace(' ', '.')] = commits[tag]
        self._generate_bar_chart(title or 'Commits by version', commits2, output, x_label_rotation=90)
        return True

    def _chart_files_type(self, title, repository, output, in_data=None, limit=20):
        """Generate pie chart with files by extension."""
        # format of lines in stdout: path/to/file.c
        stdout = self._git_command(repository, ['git', 'ls-tree', '-r', '--name-only', 'HEAD'])
        extensions = {}
        for line in stdout:
            ext = os.path.splitext(line)[1]
            if not ext:
                ext = '(no extension)'
            extensions[ext] = extensions.get(ext, 0) + 1
        pie_chart = pygal.Pie(style=self.style, truncate_legend=100, value_font_size=12)
        pie_chart.title = title or 'Files by extension'
        count = 0
        count_others = 0
        sum_others = 0
        for ext in sorted(extensions, key=extensions.get, reverse=True):
            count += 1
            if limit <= 0 or count <= limit:
                pie_chart.add('%s (%d)' % (ext, extensions[ext]), extensions[ext])
            else:
                count_others += 1
                sum_others += extensions[ext]
        if count_others:
            pie_chart.add('%d others (%d)' % (count_others, sum_others), sum_others)
        pie_chart.render_to_file(output)
        return True

    def generate(self, name, title, repository, output, in_data=None):
        """Generate a chart, and return True if OK, False if error."""
        if not name in self.charts:
            return False
        try:
            return self.charts[name](title, repository, output, in_data)
        except:
            print ('Error:\n%s' % traceback.print_exc())
            return False

chart = GitChart()

if len(sys.argv) < 4:
    print('')
    print('gitchart.py %s (C) 2013 Sebastien Helleu <flashcode@flashtux.org>' % VERSION)
    print('')
    print('Syntax:')
    print('  %s <chart> <title> <repository> <output>' % sys.argv[0])
    print('')
    print('    chart       name of chart, one of: %s' % ', '.join(chart.charts))
    print('    title       title of chart')
    print('    repository  directory with git repository')
    print('    output      output path/filename (file.svg)')
    print('')
    sys.exit(1)

# read data on standard input
in_data = None
inr, outr, exceptr = select.select([sys.stdin], [], [], 0)
if inr:
    in_data = os.read(sys.stdin.fileno(), 1024 * 1024)  # read max 1MB

if not chart.generate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], in_data=in_data):
    print('Failed to generate chart: %s' % sys.argv)
