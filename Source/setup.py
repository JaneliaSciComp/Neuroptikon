"""
py2app/py2exe build script for Neuroptikon

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe
"""

import wxversion
wxversion.select('2.8')

app_scripts = ['Neuroptikon.py']
setup_options = dict()

resources = ['Images', 'Inspectors', 'Ontologies', 'Scripts', 'Textures']

import sys
if sys.platform == 'darwin':
	setup_options['setup_requires'] = ['py2app']
	setup_options['app'] = app_scripts
	
	py2app_options = dict()
	
	py2app_options['packages'] = ['wx']
	
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

from setuptools import setup
setup(
	name='Neuroptikon', 
	**setup_options
)

# Strip out any .pyc or .pyo files.
import os
for root, dirs, files in os.walk('dist' + os.sep + 'Neuroptikon.app', topdown=False):
    for name in files:
    	if os.path.splitext(name)[1] in ['.pyc', '.pyo']:
	        os.remove(os.path.join(root, name))
