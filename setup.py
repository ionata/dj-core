#!/usr/bin/env python
from __future__ import absolute_import, print_function

import io

from setuptools import setup, find_packages


def _read(filename, as_lines=True):
    with io.open(filename, encoding='utf-8') as handle:
        if as_lines:
            return [line.strip('\n').strip() for line in handle.readlines()]
        return handle.read()


setup(
    name='dj-core',
    version='0.1.2',
    description='A self-contained and extensible Django environment',
    long_description=_read('README.md', as_lines=False),
    author='Ionata Digital',
    author_email='webmaster@ionata.com.au',
    url='https://github.com/ionata/dj-core',
    packages=find_packages(),
    include_package_data=True,
    install_requires=_read('requirements-production.txt'),
    extras_require={
        'defaults': _read('requirements-defaults.txt'),
    },
    python_requires='>=2.7,>=3.5',
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
