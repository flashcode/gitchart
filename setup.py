# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2020 Sébastien Helleu <flashcode@flashtux.org>
#
# This file is part of gitchart.
#
# Gitchart is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Gitchart is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gitchart.  If not, see <https://www.gnu.org/licenses/>.
#

from setuptools import setup

DESCRIPTION = 'Generate statistic charts on Git repositories.'
LONG_DESCRIPTION = """
Gitchart can generate following charts:

* authors,
* processed tickets by author,
* commits by hour of day,
* commits by hour of week,
* commits by day,
* commits by day of week,
* commits by month of year,
* commits by year,
* commits by year/month,
* commits by tag/version,
* files by type (extension).
"""

setup(
    name='gitchart',
    version='1.4-dev',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Sébastien Helleu',
    author_email='flashcode@flashtux.org',
    url='https://github.com/flashcode/gitchart',
    license='GPL3',
    keywords='git chart pygal',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 '
        'or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Version Control',
    ],
    packages=['.'],
    install_requires=['pygal'],
    entry_points={
        'console_scripts': ['gitchart=gitchart:main'],
    }
)
