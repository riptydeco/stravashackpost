#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Craig Jones",
    author_email='riptyde@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Contains the code for creating a weekly fitness post on Shacknews.com from Strava data.",
    entry_points={
        'console_scripts': [
            'stravashackpost=stravashackpost.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='stravashackpost',
    name='stravashackpost',
    packages=find_packages(include=['stravashackpost', 'stravashackpost.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/riptydeco/stravashackpost',
    version='0.1.0',
    zip_safe=False,
)
