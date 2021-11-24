#!/usr/bin/env python3
#
# Copyright (C) 2013-2021 Sébastien Helleu <flashcode@flashtux.org>
#
# This file is part of Gitchart.
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
# along with Gitchart.  If not, see <https://www.gnu.org/licenses/>.
#

from codecs import open
from setuptools import setup, find_packages
from gitchart import __version__ as gitchart_version

DESCRIPTION = 'Generate statistic charts on Git repositories.'

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='gitchart',
    version=gitchart_version,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type='text/markdown',
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
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Version Control',
    ],
    packages=find_packages(),
    install_requires=[
        'pygal',
    ],
    entry_points={
        'console_scripts': ['gitchart=gitchart:main'],
    }
)
