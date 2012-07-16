import os
import sys

from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))

def _read(path):
    with open(path) as f:
        data= f.read()

    f.close()

    return data

README = _read(os.path.join(here, 'README.md'))
CHANGES = _read(os.path.join(here, 'CHANGES.txt'))

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
      version='0.6',
      description='pyramid_webassets',
      long_description=README + '\n\n' +  CHANGES,
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
      install_requires = requires,
      test_requires = ['pytest', 'mock', 'unittest2'],
      cmdclass = {'test': PyTest},
      paster_plugins=['pyramid'],
      )

