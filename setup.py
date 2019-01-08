#!/usr/bin/env python3
import os
from codecs import open
from sys import version_info

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

assert version_info >= (3, 6, 1), 'Pythonic CUPS requires Python >=3.0.0'

INSTALL_DEPS = [
    '',
    ]

about = {}
with open(os.path.join(here, 'src', 'pcups', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description='\n\n'.join([open('README.md').read(), open('CHANGES.md').read()]),
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    license=about['__license__'],
    url=about['__url__'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'': ['LICENSE']},
    install_requires=INSTALL_DEPS,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
    ],
)
