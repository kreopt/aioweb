#!/usr/bin/env python3
import os

from distutils.core import setup

from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    requirements = f.readlines()

setup(name='aioweb',
      version='0.1',
      description='asyncronous web framework',
      author='kreopt',
      author_email='kreopt@gmail.com',
      url='https://github.com/kreopt/aioweb/',
      packages=find_packages(exclude=tuple('test')),
      include_package_data=True,
      install_requires=requirements,
      extras_require={
              'dev': ['aiohttp-devtools', 'aiohttp_debugtoolbar'],
              'test': ['pytest-asyncio'],
      },
     )