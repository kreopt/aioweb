#!/usr/bin/env python3
import os
import shutil

from distutils.core import setup

from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'requirements.txt')) as f:
    requirements = f.readlines()

data_files = []
for root, dirs, files in os.walk("generators"):
    if len(files) != 0:
        data_files.append((root, list(map(lambda f: os.path.join(root, f), files))))

print(data_files)

# from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        install.run(self)

        WYRM_PATH = os.path.join(self.install_scripts, 'wyrm')
        AIOWEB_SHARE = os.path.join(self.install_base, 'share/aioweb/')

        print("creating %s" % WYRM_PATH)

        if os.path.exists(WYRM_PATH):
            os.unlink(WYRM_PATH)

        shutil.copy2("bin/wyrm", self.install_scripts)

        print("coping generators")

        if os.path.exists(AIOWEB_SHARE):
            shutil.rmtree(AIOWEB_SHARE)
        os.mkdir(AIOWEB_SHARE)

        shutil.copytree("generators", os.path.join(AIOWEB_SHARE, "generators"))


setup(name='aioweb',
      version='0.1',
      description='asyncronous web framework',
      author='kreopt',
      author_email='kreopt@gmail.com',
      url='https://github.com/kreopt/aioweb/',
      # scripts=['bin/wyrm'],
      packages=find_packages(include=('aioweb',)),
      include_package_data=True,
      install_requires=requirements,
      extras_require={
          'dev': ['aiohttp-devtools', 'aiohttp_debugtoolbar'],
          'test': ['pytest-asyncio'],
      },
      data_files=data_files,
      cmdclass={'install': CustomInstallCommand}

      )
