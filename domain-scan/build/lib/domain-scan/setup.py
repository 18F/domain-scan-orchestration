#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

description = 'domain scanning utility'
with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name = 'domain-scan',
    version = '0.1',
    url = 'https://github.com/18f/domain-scan',
    license = 'CC0 1.0 Universal',
    description = description,
    long_description = long_description,
    author = 'Eric Mill',
    author_email = 'eric.mill@gsa.gov',
    install_requires = [
        'ipython',
        'requests',
        'strict-rfc3339',
        'sslyze',
        'cryptography',
        'censys',
        'six'
    ],
    packages = ['domain-scan'],
    package_dir={'domain-scan': 'domain-scan'},
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
)
