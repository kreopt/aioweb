#!/usr/bin/env python3

from setuptools import setup

from setuptools import find_packages

setup(name='aioweb',
      version='0.1',
      description='asyncronous web framework',
      author='kreopt',
      author_email='kreopt@gmail.com',
      url='https://github.com/kreopt/aioweb/',
      packages=find_packages(exclude=tuple('test')),
      include_package_data=True,
      install_requires=[
            'aiohttp',
            'aiohttp_jinja2',
            'aiohttp_security',
            'aioredis',
            'aiosmtplib',
            'aiohttp_session',
            'aiofiles',
            'passlib',
            'pycrypto',
            'orator',
            'pyyaml'
      ],
      extras_require={
              'dev': ['aiohttp-devtools', 'aiohttp_debugtoolbar'],
              'test': ['pytest-asyncio'],
      },
     )