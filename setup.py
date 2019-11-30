#!/usr/bin/env python

from setuptools import setup, find_packages
import re

# parse version from init.py
with open("maptools/__init__.py") as init:
    CUR_VERSION = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        init.read(),
        re.M,
    ).group(1)

# run setup script
setup(
    name="maptools",
    version=CUR_VERSION,
    url="https://github.com/j-meek",
    author="Jared Meek and Deren Eaton",
    author_email="jared.meek@columbia.edu",
    description="maps maps maps",
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=[
        "future",
        "pandas", 
        "numpy", 
        "folium",
        "beautifulsoup4",
        "requests"
    ],
    keywords="map tool",
    entry_points={},
    data_files=[],
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Framework :: Jupyter'        
    ],
)
