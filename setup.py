#!/usr/bin/env python

from setuptools import setup, find_packages


requirements = [
]

requirements_tests = [
]

setup(
    name='colejorz',
    version='0.0.0',
    description='To be determined.',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requirements,
    extras_require={
        'tests': requirements_tests
    },
    entry_points={
        'console_scripts': [
            'colejorz = colejorz.stationmaster:main',
        ]
    }
)
