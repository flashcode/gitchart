#
# SPDX-FileCopyrightText: 2021-2025 Sébastien Helleu <flashcode@flashtux.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of GitChart.
#
# GitChart is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# GitChart is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GitChart.  If not, see <https://www.gnu.org/licenses/>.
#

all: check

check: lint

lint: flake8 pylint

flake8:
	flake8 . --count --select=E9,F63,F7,F82 --ignore=E203,W503 --show-source --statistics
	flake8 . --count --ignore=E203,W503 --exit-zero --max-complexity=10 --statistics

pylint:
	pylint gitchart
