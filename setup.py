from setuptools import setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read().replace('.. :changelog:', '')

setup(
    name='gitchart',
    version='0.0.3',
    description='Build SVG charts from a git repository',
    long_description=readme + '\n\n' + history,
    author=u'S\xe9bastien Helleu',
    author_email='flashcode@flashtux.org',
    maintainer='Thomas Grainger',
    maintainer_email='gitchart@graingert.co.uk',
    license='GPLv3+',
    url='https://github.com/gitchart/gitchart',
    py_modules=['gitchart'],
    install_requires=['pygal'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        (
            'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)'
        ),
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': ['gitchart=gitchart:main'],
    },
)
