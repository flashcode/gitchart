# SPDX-FileCopyrightText: 2021-2026 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

all: check

check: lint test

lint: ruff ty

ruff:
	uvx ruff check

ty:
	uvx ty check

test:
	uv run pytest -vv --cov=src/gitchart --cov-report=term-missing
