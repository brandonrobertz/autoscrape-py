#!/usr/bin/env python
from os import path
import setuptools

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements


def load_requirements(fname):
    BASEDIR = path.abspath(path.dirname(__file__))
    filepath = path.join(BASEDIR, fname)
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]


def get_long_description():
    BASEDIR = path.abspath(path.dirname(__file__))
    with open(path.join(BASEDIR, 'README.rst'), encoding='utf-8') as f:
        return f.read()


setuptools.setup(
    name='autoscrape',
    version='1.1.3',
    description='An automated, programming-free web scraper for interactive sites',
    long_description=get_long_description(),
    author='Brandon Roberts',
    author_email='brandon@bxroberts.org',
    url='https://github.com/brandonrobertz/autoscrape-py',
    license='AGPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=[
        'autoscrape',
        'autoscrape.cli',
        'autoscrape.util',
        'autoscrape.backends',
        'autoscrape.backends.base',
        'autoscrape.backends.selenium',
        'autoscrape.backends.requests',
        'autoscrape.backends.warc',
        'autoscrape.scrapers',
        'autoscrape.search',
    ],
    entry_points={
        'console_scripts': [
            'autoscrape = autoscrape.cli.scrape:main',
        ]
    },
    install_requires=load_requirements("requirements.txt"),
)
