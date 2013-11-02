## Description

`gitchart.py` is a Python script to build charts from a Git repository.

It can build following charts, as SVG or PNG:

* authors (pie chart)
* commits by hour, day of week, month of year, year, year/month (bar charts)
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
