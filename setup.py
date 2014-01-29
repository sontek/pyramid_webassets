#!/usr/bin/env python

import os

from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as fp:
    README = fp.read()

with open(os.path.join(here, 'CHANGES.txt')) as fp:
    CHANGES = fp.read()

#requires = open('requirements.txt').readlines()
requires = ['pyramid>=1.3', 'webassets>=0.7.1', 'zope.interface']

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import subprocess
        errno = subprocess.call('py.test')
        raise SystemExit(errno)

setup(name='pyramid_webassets',
      version='0.7.2',
      description='pyramid_webassets',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='John Anderson',
      author_email='sontek@gmail.com',
      url='http://github.com/sontek/pyramid_webassets',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyramid_webassets',
      install_requires=requires,
      tests_require=['pytest', 'mock', 'unittest2'],
      cmdclass={'test': PyTest},
      )
