## Description

`gitchart.py` is a Python script to build charts from a Git repository.

It can build following charts, as SVG or PNG:

* authors (pie chart)
* commits by hour of day, day, day of week, month of year, year, year/month
  (bar charts)
* commits by hour of week (dot chart)
* files by type (pie chart)

## Install

The script requires Python >= 2.7 and [Pygal](http://pygal.org/), which can be
installed with this command:

    # pip install pygal

Note: cairosvg is required to generate PNG files.

## Usage

See output of command:

    $ python gitchart.py -h

## Examples

Generate pie chart with authors:

    $ python gitchart.py -t "Git authors on project X" -r /path/to/gitrepo/ authors authors.svg

Generate bar chart with commits by year:

    $ python gitchart.py -r /path/to/gitrepo/ commits_year commits_year.svg

Generate bar chart with commits by version (tag):

    $ cd /path/to/gitrepo/
    $ git tag | python /path/to/gitchart.py commits_version /tmp/commits_version.svg

## Demo

`gitchart.py` is used to build statistics for WeeChat: http://weechat.org/dev/stats/

## Copyright

Copyright (C) 2013-2016 Sébastien Helleu <flashcode@flashtux.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
