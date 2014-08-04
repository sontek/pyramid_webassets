#!/usr/bin/env python

import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as fp:
    README = fp.read()

with open(os.path.join(here, 'CHANGES.txt')) as fp:
    CHANGES = fp.read()

#requires = open('requirements.txt').readlines()
requires = ['pyramid>=1.3', 'webassets>=0.8', 'zope.interface', 'six>=1.4.1']

extras_require = {
    'bundles-yaml': 'PyYAML>=3.10',
}


class PyTest(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)

setup(name='pyramid_webassets',
      version='0.8',
      description='pyramid_webassets',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "License :: OSI Approved :: MIT License",
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
      extras_require=extras_require,
      tests_require=['tox'],
      cmdclass={'test': PyTest},
      )
