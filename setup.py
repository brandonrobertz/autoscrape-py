#!/usr/bin/env python
from os import path
import setuptools


def get_long_description():
    BASEDIR = path.abspath(path.dirname(__file__))
    with open(path.join(BASEDIR, 'README.rst'), encoding='utf-8') as f:
        return f.read()


setuptools.setup(
    name='autoscrape',
    version='1.2.7',
    description='An automated, programming-free web scraper for interactive sites',
    long_description=get_long_description(),
    author='Brandon Roberts',
    author_email='brandon@bxroberts.org',
    url='https://github.com/brandonrobertz/autoscrape-py',
    license='AGPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
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
        'autoscrape.vectorization',
    ],
    entry_points={
        'console_scripts': [
            'autoscrape = autoscrape.cli.scrape:main',
        ]
    },
    install_requires=[
        'lxml>=4.3.0',
        'html5lib>=1.0.1',
        'docopt>=0.6.2',
        'cssselect>=1.1.0',
        'requests>=2.22.0',
    ],
    extras_require={
        'selenium-backend': [
            'selenium>=3.141.0'
        ],
        'warc-backend': [
            'warc3-wet>=0.2.3',
            'plyvel==1.2.0',
        ],
        'embeddings-vectorizer': [
            'numpy>=1.15.0'
        ],

        'graph': [
            'networkx>=2.2',
        ],
        'all': [
            'selenium>=3.141.0'
            'networkx>=2.2',
            'numpy>=1.15.0',
            'warc3-wet>=0.2.3',
            'plyvel==1.2.0',
        ],
    }
)
