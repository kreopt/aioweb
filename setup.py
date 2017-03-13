#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(name='aioweb',
      version='0.1',
      description='asyncronous web framework',
      author='kreopt',
      author_email='kreopt@gmail.com',
      url='https://github.com/kreopt/aioweb/',
      packages=find_packages(),
     )