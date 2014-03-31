#!/usr/bin/env python3
from distutils.core import setup

setup(
    name='BatteryMeter',
    version='0.1.0',
    description='A Battery Meter icon on the systray / system tray.',
    author='Mizki SUZUMORI',
    author_email='mizki9577@gmail.com',
    url='https://github.com/mizki9577/BatteryMeter',
    scripts=['batmeter'],
    data_files=[('share/batmeter', ['font.png'])],
    license='2-Clause BSD',
)
