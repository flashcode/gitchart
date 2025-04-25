<!--
SPDX-FileCopyrightText: 2016-2025 Sébastien Helleu <flashcode@flashtux.org>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Gitchart ChangeLog

## Version 2.0.2 (2021-11-24)

### Fixed

- Fix CI

## Version 2.0.1 (2021-11-24)

### Added

- Add `gitchart` module

## Version 2.0.0 (2021-11-24)

### Changed

- **Breaking**: drop Python 2 support, Python 3.6 is now required
- Convert README and ChangeLog to markdown

### Added

- Add option `-S` / `--style` to choose Pygal style, defaults to custom style `gitchart_light`

## Version 1.5 (2020-03-07)

### Changed

- Switch from Travis CI to GitHub actions

### Added

- Add file requirements.txt

## Version 1.4 (2019-07-13)

### Added

- Add chart `tickets_author`
- Add option `-m` / `--no-merges` to not count merge commits in git log commands
- Add setup.py

## Version 1.3 (2016-08-13)

### Changed

- **Breaking**: add argument `--all` for git log commands

### Fixed

- Fix check of javascript command line argument ([#3](https://github.com/flashcode/gitchart/issues/3))

## Version 1.2 (2014-12-06)

### Added

- Add option `-j` / `--js` to customize javascript files/links

### Fixed

- Fix the working directory for the second git command

## Version 1.1 (2014-04-18)

### Fixed

- Fix PEP8 warnings

## Version 1.0 (2013-11-10)

### Fixed

- Fix parsing of authors

## Version 0.9 (2013-11-10)

### Fixed

- Ignore UTF-8 decoding errors

## Version 0.8 (2013-11-10)

### Changed

- **Breaking**: rename chart `commits_hour` to `commits_hour_day` and `commits_day` to `commits_day_week`
- **Breaking**: rename option `-m` / `--max` to `-d` / `--max-diff`

### Added

- Add chart "commits_day"
- Add option `-s` / `--sort-max`

## Version 0.7 (2013-11-09)

### Fixed

- Fix chart title

## Version 0.6 (2013-11-08)

### Changed

- Add a main function

## Version 0.5 (2013-11-02)

### Changed

- Make options title/repository optional
- Display SVG on standard output if filename is "-"

### Added

- Add option `-m` / `--max`

## Version 0.4 (2013-10-25)

### Added

- Add PNG support

## Version 0.3 (2013-03-21)

### Changed

- Fill months without commits (set value to 0) in chart `commits_year_month`

## Version 0.2 (2013-03-16)

### Changed

- Read all data on standard input (no more limit at 1MB)

### Fixed

- Add missing argument `title` in help

## Version 0.1 (2013-03-15)

### Added

- First release
