"""
py2app/py2exe build script for Neuroptikon

Usage (Mac OS X):
    python setup.py --quiet py2app

Usage (Windows):
    python setup.py --quiet py2exe
"""

# Make sure setuptools is installed.
import ez_setup
ez_setup.use_setuptools()

import os, sys
from setuptools import setup

app_scripts = ['Neuroptikon.py']
app_version = '0.9.2'	# TBD: will this already by set in wx for the app?

setup_options = dict()

resources = ['Images', 'Inspectors', 'Layouts', 'Neuroptikon_v1.0.xsd', 'Ontologies', 'Textures']
includes = ['wx', 'xlrd']
excludes = ['Inspectors', 'Layouts', 'matplotlib', 'scipy']

sys.path.append('lib/CrossPlatform')

if sys.platform == 'darwin':

    # Mac build notes:
    # 1. Install Python from http://www.python.org/ftp/python/2.5.4/python-2.5.4-macosx.dmg
    # 2. Make that python active: sudo python_select python25 (?)
    # 3. sudo easy_install py2app
    # 4. sudo easy_install numpy
    # 5. Install wxPython from http://downloads.sourceforge.net/wxpython/wxPython2.8-osx-unicode-2.8.9.2-universal-py2.5.dmg
    # 6. export PYTHONPATH=/usr/local/lib/wxPython-unicode/lib/python2.5/site-packages:/Library/Python/2.5
    # 7. python setup.py py2app
    
    import wxversion
    wxversion.select('2.8')
    
    sys.path.append('lib/Darwin')
    
    setup_options['setup_requires'] = ['py2app']
    setup_options['app'] = app_scripts
    
    py2app_options = dict()
    
    dist_dir = 'build/Neuroptikon ' + app_version
    py2app_options['dist_dir'] = dist_dir
    
    py2app_options['packages'] = includes
    py2app_options['excludes'] = excludes
    
    resources.append('../Artwork/Neuroptikon.icns')
    resources.append('lib/Darwin/fdp')
    resources.append('lib/Darwin/graphviz')
    resources.append('lib/Darwin/osgdb_qt.so')
    py2app_options['resources'] = ','.join(resources)
    
    py2app_options['argv_emulation'] = True
    py2app_options['plist'] = dict()
    py2app_options['plist']['CFBundleIconFile'] = 'Neuroptikon.icns'
    py2app_options['plist']['PyResourcePackages'] = ['lib/python2.5/lib-dynload']
    py2app_options['plist']['LSEnvironment'] = dict(DYLD_LIBRARY_PATH = '../Resources')
    
    setup_options['options'] = dict(py2app = py2app_options)
    
elif sys.platform == 'win32':
    
    # Windows build notes:
    # - Install Enthought Python Distribution
    # - Install Inno Setup QuickStart Pack from http://jrsoftware.org/isdl.php
    # - move aside networkx(?) and pyxml site-packages
    # - python setup.py py2exe
    
    import py2exe
    
    sys.path.append('lib/Windows')
    
    setup_options['setup_requires'] = ['py2exe']
    setup_options['windows'] = [{'script': app_scripts[0], 'icon_resources':  [(0, '../Artwork/Neuroptikon.ico')]}]
    
    py2exe_options = dict()
    
    dist_dir = 'build/Neuroptikon ' + app_version
    py2exe_options['dist_dir'] = dist_dir
    
    py2exe_options['packages'] = includes
    py2exe_options['excludes'] = excludes + ['numarray', 'pyxml', 'Tkinter', '_tkinter']
    
    # py2exe doesn't support 'resources' so we have to add each file individually.
    # TODO: use glob instead?
    def addDataFiles(dataFilesList, dataDir):
        dataFiles = []
        for dataFileName in os.listdir(dataDir):
            dataFilePath = dataDir + os.sep + dataFileName
            if dataFileName != '.svn':
                if os.path.isdir(dataFilePath):
                    addDataFiles(dataFilesList, dataFilePath)
                else:
                    dataFiles.append(dataFilePath)
        if len(dataFiles) > 0:
            dataFilesList.append((dataDir, dataFiles))
    
    resources.append('Scripts')	# TBD: or add them via the installer?
    dataFilesList = []
    for resourceName in resources:
        if os.path.isdir(resourceName):
            addDataFiles(dataFilesList, resourceName)
        else:
            dataFilesList.append(('', [resourceName]))
    # Include all of the libraries that OSG needs.
    dataFilesList.append(('', ['lib/Windows/freetype6.dll', 'lib/Windows/libimage.dll', 'lib/Windows/libpng3.dll', 'lib/Windows/libpng12.dll', 'lib/Windows/librle3.dll', 'lib/Windows/libtiff3.dll']))
    # Include the OSG plug-ins we use.
    dataFilesList.append(('', ['lib/Windows/osgdb_jpeg.dll', 'lib/Windows/osgdb_png.dll', 'lib/Windows/osgdb_tiff.dll']))
    setup_options['data_files'] = dataFilesList
    
    setup_options['options'] = dict(py2exe = py2exe_options)
else:
        pass	# TODO: Linux setup

setup(
    name = 'Neuroptikon', 
    version = app_version, 
    description = 'Neural circuit visualization', 
    url = 'http://openwiki.janelia.org/wiki/display/neuroptikon/', 
    **setup_options
)


if sys.platform == 'darwin':
    import shutil
    scriptsDir = os.path.join(dist_dir, 'Sample Scripts')
    if os.path.exists(scriptsDir):
        shutil.rmtree(scriptsDir)
    shutil.copytree('Scripts', scriptsDir)


# Strip out any .pyc or .pyo files.
import os
for root, dirs, files in os.walk(dist_dir, topdown=False):
    for name in files:
        if os.path.splitext(name)[1] in ['.pyc', '.pyo']:
                os.remove(os.path.join(root, name))


from subprocess import call
if sys.platform == 'darwin':
    # Create the disk image
    dmgPath = 'build/Neuroptikon ' + app_version + '.dmg'
    if os.path.exists(dmgPath):
        os.remove(dmgPath)
    print 'Creating disk image...'
    print 'hdiutil create -srcfolder \'' + dist_dir + '\' -format UDZO "' + dmgPath + '"'
    retcode = call('hdiutil create -srcfolder \'' + dist_dir + '\' -format UDZO "' + dmgPath + '"', shell=True)
    if retcode < 0:
        print "Could not create disk image"
    else:
        # Open the disk image in the Finder so we can check it out.
        call('open "' + dmgPath + '"', shell=True)
elif sys.platform == 'win32':
    # Create the installer
    print 'Creating installer...'
    retcode = call('C:\Program Files\Inno Setup 5\iscc.exe /Q /O"build" "/dAPP_VERSION=' + app_version + '" Neuroptikon.iss')
    if retcode != 0:
        print "Could not create the installer"
