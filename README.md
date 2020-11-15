# Gitchart

[![PyPI](https://img.shields.io/pypi/v/gitchart.svg)](https://pypi.org/project/gitchart/)
[![Build Status](https://github.com/flashcode/gitchart/workflows/CI/badge.svg)](https://github.com/flashcode/gitchart/actions?query=workflow%3A%22CI%22)

Gitchart is a Python script to build charts from a Git repository.

It can build following charts, as SVG or PNG:

- authors, processed tickets by author (pie charts)
- commits by hour of day, day, day of week, month of year, year, year/month (bar charts)
- commits by hour of week (dot chart)
- files by type (pie chart)

## Requirements

Gitchart requires:

- Python ≥ 3.6
- [Pygal](http://www.pygal.org/) (`pip install pygal`)

Optional dependencies:

- cairosvg, to generate PNG files

## Install

You can install Gitchart with this command from the source repository:

```
$ python setup.py install
```

## Usage

See output of command:

```
$ gitchart -h
```

## Examples

Generate pie chart with authors:

```
$ gitchart -t "Git authors on project X" -r /path/to/gitrepo/ authors authors.svg
```

Generate bar chart with commits by year:

```
$ gitchart -r /path/to/gitrepo/ commits_year commits_year.svg
```

Generate bar chart with commits by version (git tag):

```
$ cd /path/to/gitrepo/
$ git tag | gitchart commits_version /tmp/commits_version.svg
```

## Demo

Gitchart is used to build statistics for WeeChat: https://weechat.org/dev/stats/

## Copyright

Copyright © 2013-2020 [Sébastien Helleu](https://github.com/flashcode)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
