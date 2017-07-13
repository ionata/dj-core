#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import setup, find_packages


with open('README.rst', 'r') as f:
    readme = f.read()


setup(
    name='dj-core',
    version='0.0.2',
    description='A self-contained and extensible Django environment',
    long_description=readme,
    author='Ionata Digital',
    author_email='webmaster@ionata.com.au',
    url='https://github.com/ionata/dj-core',
    packages=find_packages('src'),
    install_requires=[
        'django-environ~=0.4.3',
        'django>=1.8.0',
    ],
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
