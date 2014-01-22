"""
Flask-OpenID
============

Adds OpenID support to Flask.

Links:

* `Flask-OpenID Documentation <http://packages.python.org/Flask-OpenID/>`_
* `Flask <http://flask.pocoo.org>`_
* `development version
  <http://github.com/mitsuhiko/flask-openid/zipball/master#egg=Flask-OpenID-dev>`_
"""
from setuptools import setup
import sys
import os

# This check is to make sure we checkout docs/_themes before running sdist
if not os.path.exists("./docs/_themes/README"):
    print 'Please make sure you have docs/_themes checked out while running setup.py!'
    if os.path.exists('.git'):
        print 'You seem to be using a git checkout, please execute the following commands to get the docs/_themes directory:'
        print ' - git submodule init'
        print ' - git submodule update'
    else:
        print 'You seem to be using a release. Please use the release tarball from PyPI instead of the archive from GitHub'
    sys.exit(1)

extra = {}
if sys.version_info >= (3,):
    install_requires = ['Flask>=0.10.1', 'python3-openid>=2.0']
    extra['use_2to3'] = True
else:
    install_requires = ['Flask>=0.3', 'python-openid>=2.0']

setup(
    name='Flask-OpenID',
    version='1.1',
    url='http://github.com/mitsuhiko/flask-openid/',
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    description='OpenID support for Flask',
    long_description=__doc__,
    py_modules=['flask_openid'],
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    **extra
)
