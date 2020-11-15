# gitchart ChangeLog

## Version 1.6 (under dev)

- Convert README and ChangeLog to markdown.

## Version 1.5 (2020-03-07)

- Switch from Travis CI to GitHub actions.
- Add file requirements.txt.

## Version 1.4 (2019-07-13)

- Add chart `tickets_author`.
- Add option `-m` / `--no-merges` to not count merge commits in git log commands.
- Add setup.py.

## Version 1.3 (2016-08-13)

- Fix check of javascript command line argument (issue #3).
- Add argument `--all` for git log commands.

## Version 1.2 (2014-12-06)

- Add option `-j` / `--js` to customize javascript files/links.
- Fix the working directory for the second git command.

## Version 1.1 (2014-04-18)

- Fix PEP8 warnings.

## Version 1.0 (2013-11-10)

- Fix parsing of authors.

## Version 0.9 (2013-11-10)

- Ignore UTF-8 decoding errors.

## Version 0.8 (2013-11-10)

- Add chart "commits_day".
- Rename chart `commits_hour` to `commits_hour_day` and `commits_day` to `commits_day_week`.
- Add option `-s` / `--sort-max`.
- Rename option `-m` / `--max` to `-d` / `--max-diff`.

## Version 0.7 (2013-11-09)

- Fix chart title.

## Version 0.6 (2013-11-08)

- Add a main function.

## Version 0.5 (2013-11-02)

- Make options title/repository optional.
- Add option `-m` / `--max`.
- Display SVG on standard output if filename is "-".

## Version 0.4 (2013-10-25)

- Add PNG support.

## Version 0.3 (2013-03-21)

- Fill months without commits (set value to 0) in chart `commits_year_month`.

## Version 0.2 (2013-03-16)

- Read all data on standard input (no more limit at 1MB).
- Add missing argument `title` in help.

## Version 0.1 (2013-03-15)

- First release.
