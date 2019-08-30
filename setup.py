#!/usr/bin/env python
"""Colejorz's installation file."""

from setuptools import setup, find_packages


requirements = [
    'pyramid==1.10.2',
]

requirements_tests = [
    'pytest',
    'pytest-cov',
    'pytest_pyramid',
]

requirements_linters = [
    'mypy',
    'pycodestyle',
    'pydocstyle',
    'pylint'
]

setup(
    name='colejorz',
    version='0.0.0',
    description='To be determined.',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'tests': requirements_tests,
        'linters': requirements_linters
    },
    entry_points={
        'console_scripts': [
            'colejorz = colejorz:serve',
        ],
    }
)
