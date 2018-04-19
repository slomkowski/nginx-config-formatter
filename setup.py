#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import codecs
from setuptools import setup, find_packages

with codecs.open('README.md', encoding='utf-8', errors='ignore') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst', encoding='utf-8', errors='ignore') as history_file:
    history = history_file.read()

requirements = [
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='nginxfmt',
    version='1.0.6',
    description="nginx config file formatter/beautifier written in Python.",
    long_description=readme + '\n\n' + history,
    author="Konrad Rotkiewicz",
    author_email='konrad.rotkiewicz@gmail.com',
    url='https://github.com/krotkiewicz/nginxfmt',
    packages=find_packages(include=['nginxfmt']),
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='nginxfmt',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={
        'console_scripts': [
            'nginxfmt=nginxfmt:main'
        ]
    },
)
