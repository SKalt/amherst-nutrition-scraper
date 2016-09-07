#! /usr/bin/env python3
from distutils.core import setup


setup(
    name='amherst-nutrition-scraper',
    author='Austin Hartzheim, revised by Steven Kalt',

    version='1.3.1',
    packages=['wok-ac'],
    license='GNU GPL v3',
    description='Download menus and nutrition data from Amherst College\'s NetNutrition website.',
    long_description=open('README.md').read(),
    url='austinhartzheim.me/projects/wok/'
)
