#!/usr/bin/env python
from __future__ import absolute_import, print_function

import io

from setuptools import setup, find_packages


with io.open('README.md', encoding='utf-8') as handle:
    readme = handle.read()


with io.open('requirements-production.txt', encoding='utf-8') as handle:
    requirements = [line.strip('\n').strip() for line in handle.readlines()]


setup(
    name='dj-core',
    version='0.0.4',
    description='A self-contained and extensible Django environment',
    long_description=readme,
    author='Ionata Digital',
    author_email='webmaster@ionata.com.au',
    url='https://github.com/ionata/dj-core',
    packages=find_packages('src'),
    install_requires=requirements,
    package_dir={'': 'src'},
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
