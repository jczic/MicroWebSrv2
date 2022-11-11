#!/usr/bin/env python
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()

setup(
	name='MicroWebSrv2',
	version='2.0.6',
	description='Embedded webserver for MicroPython and CPython',
	long_description=README,
	author='Jean-Christophe Bos',
	author_email='jczic.bos@gmail.com',
	url='https://github.com/jczic/MicroWebSrv2',
	download_url='https://github.com/jczic/MicroWebSrv2/archive/master.zip',
	packages=find_packages(),
	classifiers=[
      	'Environment :: Web Environment',
      	'Topic :: Internet :: WWW/HTTP',
      	'Topic :: Software Development :: Libraries',
      	'Topic :: Software Development :: Embedded Systems',
      	'Programming Language :: Python',
      	'Programming Language :: Python :: 3',
      	'Programming Language :: Python :: Implementation :: CPython',
      	'Programming Language :: Python :: Implementation :: MicroPython',
      	'License :: OSI Approved :: MIT License',
      	'Development Status :: 5 - Production/Stable',
  	],
 )
