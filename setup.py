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
    install_requires=[
        'Flask>=0.10.1',
        'python3-openid>=3.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
