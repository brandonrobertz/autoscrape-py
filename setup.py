#!/usr/bin/env python
from os import path
import setuptools
import sys


install_requires = [
    'html5lib>=1.0.1',
    'selenium>=2.12.0',
    'webencodings>=0.5.1',
    'docopt>=0.6.2',
    'networkx>=2.2',
    'numpy>=1.15.0',
    'cssselect>=1.1.0',
    'requests>=2.22.0',
    'lxml>=4.4.2',
]


install_dev_requires = [
    # For the frontend UX
    'Flask>=1.0.2',
    'celery>=4.1.1',
    'psycopg2>=2.7.6.1',
    'flask-sqlalchemy>=2.3.2',
    'six>=1.11.0',
]


def get_long_description():
    BASEDIR = path.abspath(path.dirname(__file__))
    with open(path.join(BASEDIR, 'README.rst'), encoding='utf-8') as f:
        return f.read()


setuptools.setup(
    name='autoscrape',
    version='1.0.0rc6',
    description='An automated, programming-free web scraper for interactive sites',
    long_description=get_long_description(),
    author='Brandon Roberts',
    author_email='brandon@bxroberts.org',
    url='https://github.com/brandonrobertz/autoscrape-py',
    # project_urls={
    #     'Documentation': 'https://csvkit.readthedocs.io/en/latest/',
    # },
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
        'autoscrape.scrapers',
        'autoscrape.search',
    ],
    entry_points={
        'console_scripts': [
            'autoscrape = autoscrape.cli.scrape:main',
        ]
    },
    install_requires=install_requires
)
