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
requires = ['pyramid', 'webassets', 'zope.interface']

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
      version='0.0',
      description='pyramid_webassets',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyramid_webassets',
      install_requires = requires,
      cmdclass = {'test': PyTest},
      paster_plugins=['pyramid'],
      )

