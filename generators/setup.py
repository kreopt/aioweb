#!/usr/bin/env python3
import os
import shutil
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
requirements = ["aioweb"]

views_files=[]
for root, dirs, files in os.walk("aioweb_APP_NAME/views"):
    if len(files) != 0:
        views_files += list(map(lambda f: os.path.join(root, f).replace("aioweb_APP_NAME/", "", 1), files))

setup(name='aioweb_APP_NAME',
      version='0.1',
      description='aioweb module',
      author='human being',
      author_email='',
      url='',
      packages=find_packages(exclude=('test_project', 'tests')),
      include_package_data=True,
      install_requires=requirements,
      package_data= {'aioweb_APP_NAME': views_files},
      )
