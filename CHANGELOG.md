<!--
SPDX-FileCopyrightText: 2016-2026 Sébastien Helleu <flashcode@flashtux.org>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Changelog

## [Unreleased]

### Added

- Add unit tests

### Changed

- Use uv, ruff and ty

## [2.0.2] - 2021-11-24

### Fixed

- Fix CI

## [2.0.1] - 2021-11-24

### Added

- Add `gitchart` module

## [2.0.0] - 2021-11-24

### Added

- Add option `-S` / `--style` to choose Pygal style, defaults to custom style `gitchart_light`

### Changed

- **Breaking**: drop Python 2 support, Python 3.6 is now required
- Convert README and ChangeLog to markdown

## [1.5] - 2020-03-07

### Added

- Add file requirements.txt

### Changed

- Switch from Travis CI to GitHub actions

## [1.4] - 2019-07-13

### Added

- Add chart `tickets_author`
- Add option `-m` / `--no-merges` to not count merge commits in git log commands
- Add setup.py

## [1.3] - 2016-08-13

### Changed

- **Breaking**: add argument `--all` for git log commands

### Fixed

- Fix check of javascript command line argument ([#3](https://github.com/flashcode/gitchart/issues/3))

## [1.2] - 2014-12-06

### Added

- Add option `-j` / `--js` to customize javascript files/links

### Fixed

- Fix the working directory for the second git command

## [1.1] - 2014-04-18

### Fixed

- Fix PEP8 warnings

## [1.0] - 2013-11-10

### Fixed

- Fix parsing of authors

## [0.9] - 2013-11-10

### Fixed

- Ignore UTF-8 decoding errors

## [0.8] - 2013-11-10

### Added

- Add chart "commits_day"
- Add option `-s` / `--sort-max`

### Changed

- **Breaking**: rename chart `commits_hour` to `commits_hour_day` and `commits_day` to `commits_day_week`
- **Breaking**: rename option `-m` / `--max` to `-d` / `--max-diff`

## [0.7] - 2013-11-09

### Fixed

- Fix chart title

## [0.6] - 2013-11-08

### Changed

- Add a main function

## [0.5] - 2013-11-02

### Added

- Add option `-m` / `--max`

### Changed

- Make options title/repository optional
- Display SVG on standard output if filename is "-"

## [0.4] - 2013-10-25

### Added

- Add PNG support

## [0.3] - 2013-03-21

### Changed

- Fill months without commits (set value to 0) in chart `commits_year_month`

## [0.2] - 2013-03-16

### Changed

- Read all data on standard input (no more limit at 1MB)

### Fixed

- Add missing argument `title` in help

## [0.1] - 2013-03-15

### Added

- First release

[Unreleased]: https://github.com/flashcode/gitchart/compare/v2.0.2...HEAD
[2.0.2]: https://github.com/flashcode/gitchart/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/flashcode/gitchart/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/flashcode/gitchart/compare/v1.5...v2.0.0
[1.5]: https://github.com/flashcode/gitchart/compare/v1.4...v1.5
[1.4]: https://github.com/flashcode/gitchart/compare/v1.3...v1.4
[1.3]: https://github.com/flashcode/gitchart/compare/v1.2...v1.3
[1.2]: https://github.com/flashcode/gitchart/compare/v1.1...v1.2
[1.1]: https://github.com/flashcode/gitchart/compare/v1.0...v1.1
[1.0]: https://github.com/flashcode/gitchart/compare/v0.9...v1.0
[0.9]: https://github.com/flashcode/gitchart/compare/v0.8...v0.9
[0.8]: https://github.com/flashcode/gitchart/compare/v0.7...v0.8
[0.7]: https://github.com/flashcode/gitchart/compare/v0.6...v0.7
[0.6]: https://github.com/flashcode/gitchart/compare/v0.5...v0.6
[0.5]: https://github.com/flashcode/gitchart/compare/v0.4...v0.5
[0.4]: https://github.com/flashcode/gitchart/compare/v0.3...v0.4
[0.3]: https://github.com/flashcode/gitchart/compare/v0.2...v0.3
[0.2]: https://github.com/flashcode/gitchart/compare/v0.1...v0.2
[0.1]: https://github.com/flashcode/gitchart/releases/tag/v0.1
