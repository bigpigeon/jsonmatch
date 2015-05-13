#!/usr/bin/env python
import os
import sys
from distutils.core import setup
from jsonmatch import __version__

setup(
    name='jsonmatch',
    version=__version__,
    description='Python json tools',
    url='',
    authon='Big Pigeon',
    author_email='bigpigeon@gmail.com',
    keywords=['jsonmatch', 'json', 'match', 're'],
    packages=['jsonmatch'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)