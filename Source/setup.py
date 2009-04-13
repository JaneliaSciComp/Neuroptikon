"""
py2app/py2exe build script for Neuroptikon

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe
"""

import sys
from setuptools import setup

app_scripts = ['Neuroptikon.py']
setup_options = dict()

resources = ['Images', 'Inspectors', 'Ontologies', 'Textures']

if sys.platform == 'darwin':
	setup_options['setup_requires'] = ['py2app']
	setup_options['app'] = app_scripts
	
	py2app_options = dict()
	
	resources.append('lib/Darwin/fdp')
	resources.append('lib/Darwin/graphviz')
	resources.append('lib/Darwin/osgdb_qt.so')
	py2app_options['resources'] = ','.join(resources)
	
	py2app_options['argv_emulation'] = True
	py2app_options['plist'] = dict()
	py2app_options['plist']['PyResourcePackages'] = ['lib/python2.5/lib-dynload']
	py2app_options['plist']['LSEnvironment'] = dict(DYLD_LIBRARY_PATH = '../Resources')
	
	setup_options['options'] = dict(py2app = py2app_options)
elif sys.platform == 'win32':
	setup_options['setup_requires'] = ['py2exe']
	setup_options['app'] = app_scripts
else:
	pass	# TODO: UNIX/Linux systems

setup(
	name='Neuroptikon', 
	**setup_options
)
