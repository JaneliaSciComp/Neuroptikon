#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
py2app/py2exe build script for Neuroptikon

Usage:
    python setup.py [--quiet]
"""

# Make sure setuptools is installed.
import ez_setup
ez_setup.use_setuptools()

import os, platform, shutil, sys
from setuptools import setup

from glob import glob

import __version__
app_version = __version__.version

setup_options = dict()

app_scripts = ['neuroptikon.py']

resources = ['Images', 'Inspectors', 'Layouts', 'Neuroptikon_v1.0.xsd', 'Ontologies', 'Shapes', 'Textures']
resources += ['display/flow_shader.vert', 'display/flow_shader.frag', 'display/cull_faces.osg']
includes = ['community', 'site']
packages = ['wx', 'xlrd']
excludes = ['Inspectors', 'Layouts', 'matplotlib', 'pygraphviz', 'scipy', 'Shapes']

sys.path += ['lib/CrossPlatform', 'lib/' + platform.system()]

if sys.platform == 'darwin':
    import wxversion
    wxversion.select('3.0')

# Purge and then rebuild the documentation with Sphinx
if os.path.exists('documentation/build'):
    shutil.rmtree('documentation/build')
try:
    import sphinx
except ImportError:
    print 'You must have sphinx installed and in the Python path to build the Neuroptikon package.  See <http://sphinx.pocoo.org/>.'
    sys.exit(1)
# Work around bug in version of Sphinx on my Mac, which uses sys.argv, even when passed this argument
sphinx_args = ['-q', '-b', 'html', 'documentation/Source', 'documentation/build/Documentation']
#Used to check mac vs windows, but seems to be a sphinx version issue instead
if sphinx.__version__ >= "1.2.3":
    saved_sys_argv = sys.argv
    sys.argv = sphinx_args
    result = sphinx.build_main(argv=sphinx_args) # python 2.7.8?
    sys.argv = saved_sys_argv
else:
    result = sphinx.main(argv=sphinx_args) # python 2.7.2?
if result != 0:
    sys.exit(result)


# Assemble the platform-specific application settings. 
if sys.platform == 'darwin':

    # Mac build notes:
    # 1. Install Python from http://www.python.org/ftp/python/2.5.4/python-2.5.4-macosx.dmg
    # 2. Make that python active: sudo python_select python25 (?)
    # 3. sudo easy_install py2app
    # 4. sudo easy_install numpy
    # 5. Install wxPython from http://downloads.sourceforge.net/wxpython/wxPython2.8-osx-unicode-2.8.9.2-universal-py2.5.dmg
    # 6. export PYTHONPATH=/usr/local/lib/wxPython-unicode/lib/python2.5/site-packages:/Library/Python/2.5
    # 7. python setup.py --quiet py2app
    
    sys.argv += ['py2app']
    setup_options['setup_requires'] = ['py2app']
    setup_options['app'] = app_scripts
    
    py2app_options = dict()
    
    dist_dir = 'build/Neuroptikon ' + app_version
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    py2app_options['dist_dir'] = dist_dir
    
    excludes += ['aetools', 'StdSuites.AppleScript_Suite']
    
    py2app_options['packages'] = packages
    py2app_options['includes'] = includes
    py2app_options['excludes'] = excludes
    
    resources += ['../Artwork/Neuroptikon.icns']
    resources += ['lib/Darwin/osgdb_freetype.so', 
                  'lib/Darwin/osgdb_osg.so',
                  'lib/Darwin/osgdb_deprecated_osg.so',
                  # I don't have osgdb_qt on my Mac right now
                  ] # TODO , 'lib/Darwin/osgdb_qt.so']
    resources += ['documentation/build/Documentation']
    py2app_options['resources'] = ','.join(resources)
    
    py2app_options['argv_emulation'] = True
    py2app_options['no_strip'] = True
    py2app_options['plist'] = dict()
    py2app_options['plist']['CFBundleIconFile'] = 'Neuroptikon.icns'
    py2app_options['plist']['PyResourcePackages'] = [
            'lib/python2.7',
            'lib/python2.7/lib-dynload',
            'lib/python2.7/site-packages.zip',
            ]
    py2app_options['plist']['LSEnvironment'] = dict(DYLD_LIBRARY_PATH = '../Resources')
    
    setup_options['options'] = dict(py2app = py2app_options)
    
elif sys.platform == 'win32':
    
    # Windows build notes:
    # - Install Enthought Python Distribution
    # - Install Inno Setup QuickStart Pack from http://jrsoftware.org/isdl.php
    # - move aside networkx(?) and pyxml site-packages
    # - python setup.py --quiet py2exe
    
    try:
        import py2exe   # pylint: disable=F0401,W0611
    except ImportError:
        print 'You must have py2exe installed and in the Python path to build the Neuroptikon package.'
        sys.exit(1)
    
    sys.argv += ['py2exe']
    setup_options['setup_requires'] = ['py2exe']
    setup_options['windows'] = [{'script': app_scripts[0], 'icon_resources':  [(0, '../Artwork/Neuroptikon.ico')]}]
    
    py2exe_options = dict()
    
    dist_dir = 'build/Neuroptikon ' + app_version
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    py2exe_options['dist_dir'] = dist_dir
    
    py2exe_options['packages'] = packages
    py2exe_options['includes'] = includes
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
    dataFilesList.append(('', ['lib/Windows/osgdb_freetype.dll', 
        'lib/Windows/osgdb_jpeg.dll', 
        'lib/Windows/osgdb_osg.dll', 
        'lib/Windows/osgdb_deprecated_osg.dll', 
        'lib/Windows/osgdb_png.dll', 
        'lib/Windows/osgdb_tiff.dll']))
    setup_options['data_files'] = dataFilesList
    
    setup_options['options'] = dict(py2exe = py2exe_options)
else:
    pass	# TODO: Linux setup


# Create the application.
setup(
    name = 'Neuroptikon', 
    version = app_version, 
    description = 'Neural circuit visualization', 
    url = 'http://openwiki.janelia.org/wiki/display/neuroptikon/', 
    **setup_options
)


# Manually copy over content not handled by the setup() call.
if sys.platform == 'darwin':
    scriptsDir = os.path.join(dist_dir, 'Sample Scripts')
    if os.path.exists(scriptsDir):
        shutil.rmtree(scriptsDir)
    shutil.copytree('Scripts', scriptsDir)
elif sys.platform == 'win32':
    shutil.copytree(os.path.join('documentation/build/Documentation'), os.path.join(dist_dir, 'Documentation'))


# Strip out any .pyc or .pyo files.
for root, dirs, files in os.walk(dist_dir, topdown=False):
    for name in files:
        if os.path.splitext(name)[1] in ['.pyc', '.pyo']:
            os.remove(os.path.join(root, name))

# Clean up references to system python library -- 2014 CMB
# TODO - replace the hard-coded link paths here with paths extracted dynamically using "otool -L"
from subprocess import call
if sys.platform == 'darwin':
    print "Translating link library path names"
    # store set of library names to translate
    path_translations = {
        # Default system python. Old way. Maybe too system specific
        '/System/Library/Frameworks/Python.framework/Versions/2.7/Python' : 'Python.framework/Versions/2.7/Python',
        # New way. Installed from python.org
        '/Library/Frameworks/Python.framework/Versions/2.7/Python' : 'Python.framework/Versions/2.7/Python',
    }
    for libname in [
                'libOpenThreads.20.dylib', 
                'libosg.100.dylib', 
                'libosgAnimation.100.dylib',
                'libosgDB.100.dylib',
                'libosgFX.100.dylib',
                'libosgGA.100.dylib',
                'libosgManipulator.100.dylib',
                'libosgSim.100.dylib',
                'libosgText.100.dylib',
                'libosgUtil.100.dylib',
                'libosgViewer.100.dylib',
                'libosgVolume.100.dylib',
            ]:
        path_translations[libname] = libname
    contentsDir = os.path.join(dist_dir, "Neuroptikon.app", "Contents")
    binaries = glob(os.path.join(contentsDir, "MacOS/python"))
    binaries.extend(glob(os.path.join(contentsDir, "Frameworks/_osg*.so")))
    binaries.extend(glob(os.path.join(contentsDir, "Resources/lib/python2.7/lib-dynload/_osg*.so")))
    for fname in binaries:
        for old, new in path_translations.iteritems():
        # print fname
            cmd = 'install_name_tool -change %s %s "%s"' % (
                old,
                '@executable_path/../Frameworks/' + new, 
                fname)
            # print cmd
            retcode = call(cmd, shell=True)
            if retcode < 0:
                print "Could not change link library name in file '" + fname + "'"

# Package up the application.
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
    retcode = call('C:\Program Files (x86)\Inno Setup 5\iscc.exe /Q /O"build" "/dAPP_VERSION=' + app_version + '" Neuroptikon.iss')
    if retcode != 0:
        print "Could not create the installer"
