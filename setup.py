#!/usr/bin/env python

from distutils.core import setup

setup(
	name='MicroWebSrv2',
	version='master',
	description='Embedded webserver for MicroPython and CPython',
	long_description='MicroWebSrv2 is the new powerful embedded Web Server for MicroPython and CPython that supports route handlers, modules like WebSockets or PyhtmlTemplate and a lot of simultaneous requests (in thousands!).',
	author='Jean-Christophe Bos',
	author_email='jcb@hc2.fr',
	url='https://github.com/jczic/MicroWebSrv2',
	download_url='https://github.com/jczic/MicroWebSrv2/archive/master.zip',
	packages=[
		'MicroWebSrv2'
	],
	classifiers=[
      	'Topic :: Software Development :: Embedded Systems',
      	'Environment :: Web Environment',
      	'Topic :: Internet :: WWW/HTTP'
  	],
 )
