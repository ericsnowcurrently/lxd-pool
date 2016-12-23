import os
from importlib import import_module
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


basedir = os.path.abspath(os.path.dirname(__file__) or '.')

# required data

package_name = 'lxd_pool'
NAME = 'lxd-pool'
SUMMARY = 'Managing a pool of LXD containers.'
AUTHOR = 'Eric Snow'
EMAIL = 'ericsnowcurrently@gmail.com'
PROJECT_URL = 'https://github.com/ericsnowcurrently/lxd-pool'
LICENSE = 'New BSD License'

#with open(os.path.join(basedir, 'README.rst')) as readme_file:
#    DESCRIPTION = readme_file.read()

# dymanically generated data

pkg = import_module(package_name)

DESCRIPTION = pkg.__doc__
VERSION = pkg.__version__

# set up packages

exclude_dirs = [
        'tests',
        ]

PACKAGES = []
for path, dirs, files in os.walk(package_name):
    if "__init__.py" not in files:
        continue
    path = path.split(os.sep)
    if path[-1] in exclude_dirs:
        continue
    PACKAGES.append(".".join(path))

# dependencies

DEPS = [#''
        #''
        ]


if __name__ == "__main__":
    kwargs = dict(
            name=NAME,
            version=VERSION,
            author=AUTHOR,
            author_email=EMAIL,
            url=PROJECT_URL,
            license=LICENSE,
            description=SUMMARY,
            long_description=DESCRIPTION,
            packages=PACKAGES,
            )
    if USING_SETUPTOOLS:
        setup_args['install_requires'] = DEPS
    else:
        setup_args['requires'] = DEPS
    setup(**kwargs)
