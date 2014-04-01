#!/usr/bin/env python3
from distutils.core import setup

setup(
    name='battery-meter',
    version='0.1.0',
    description='A battery meter icon on the systray / system tray.',
    author='Mizki SUZUMORI',
    author_email='mizki9577@gmail.com',
    url='https://github.com/mizki9577/battery-meter',
    py_modules=['batterymeter.batterymeter'],
    scripts=['bin/batterymeter'],
    license='2-Clause BSD',
)
