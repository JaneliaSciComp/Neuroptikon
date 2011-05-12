#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

"""
Neuroptikon is a tool for interactive neural circuit visualization.
"""

import os, platform, sys

# Turn off OSG warnings.
if 'OSG_NOTIFY_LEVEL' not in os.environ:
    os.environ['OSG_NOTIFY_LEVEL'] = 'ALWAYS'

runningFromSource = not hasattr(sys, "frozen")

# Calculate the root directory and make sure sys.path and DYLD_LIBRARY_PATH/PATH are set up correctly.
if not runningFromSource:
    rootDir = os.path.dirname(sys.executable)
    if platform.system() == 'Darwin':
        rootDir = os.path.dirname(rootDir) + os.sep + 'Resources'
    elif platform.system() == 'Windows':
        sys.path.append(rootDir)
    platformLibPath = rootDir
else:
    rootDir = os.path.abspath(os.path.dirname(__file__))
    
    # Make sure that the library paths are set up correctly for the current location.
    commonLibPath = os.path.join(rootDir, 'lib', 'CrossPlatform')

    if platform.system() == 'Darwin':
        platformLibPath = os.path.join(rootDir, 'lib', 'Darwin')
        libraryEnvVar = 'DYLD_LIBRARY_PATH'
    elif platform.system() == 'Windows':
        platformLibPath = os.path.join(rootDir, 'lib', 'Windows')
        libraryEnvVar = 'PATH'
    else:
        platformLibPath = None
        libraryEnvVar = None

    if libraryEnvVar and (libraryEnvVar not in os.environ or platformLibPath not in os.environ[libraryEnvVar].split(os.pathsep)):
        # Add the search path for the native libraries to the enviroment.
        if libraryEnvVar in os.environ:
            os.environ[libraryEnvVar] = platformLibPath + os.pathsep + os.environ[libraryEnvVar]
        else:
            os.environ[libraryEnvVar] = platformLibPath
        # Restart this script with the same instance of python and the same arguments.
        if 'DEBUG' in os.environ:
            print 'Restarting with corrected ' + libraryEnvVar
        arguments = [sys.executable]
        arguments.extend(sys.argv)
        os.system(' '.join(arguments))
        raise SystemExit

    sys.path.insert(0, commonLibPath)
    for eggPath in os.listdir(commonLibPath):
        if eggPath.endswith('.egg'):
            sys.path.insert(0, os.path.join(commonLibPath, eggPath))
    if platformLibPath:
        sys.path.insert(0, platformLibPath)
        for eggPath in os.listdir(platformLibPath):
            if eggPath.endswith('.egg'):
                sys.path.insert(0, os.path.join(platformLibPath, eggPath))

    # TODO: figure out if it's worth packaging psyco...
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass


# Make sure fonts are found on Mac OS X
if platform.system() == 'Darwin':
    fontPaths = []
    try:
        from Carbon import File, Folder, Folders
        domains = [Folders.kUserDomain, Folders.kLocalDomain, Folders.kSystemDomain]
        if not runningFromSource:
            domains.append(Folders.kNetworkDomain)
        for domain in domains:
            try:
                fsref = Folder.FSFindFolder(domain, Folders.kFontsFolderType, False)
                fontPaths.append(File.pathname(fsref))
            except:
                pass    # Folder probably doesn't exist.
    except:
        fontPaths.extend([os.path.expanduser('~/Library/Fonts'), '/Library/Fonts', '/Network/Library/Fonts', '/System/Library/Fonts'])
    os.environ['OSG_FILE_PATH'] = ':'.join(fontPaths)


# Set up for internationalization.
import gettext as gettext_module, __builtin__
__builtin__.gettext = gettext_module.translation('Neuroptikon', fallback = True).lgettext


# Install a new version of inspect.getdoc() that converts any reST formatting to plain text.
import inspect, re
_orig_getdoc = inspect.getdoc
def _getdoc(pyObject):
    docstring = _orig_getdoc(pyObject)
    if docstring:
        # Convert any interpreted text to plain text.  <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#interpreted-text>
        docstring = re.sub(r':[^:]+:`([^<]*) \<.*\>`', r'\1', docstring)
        docstring = re.sub(r':[^:]+:`([^<]*)`', r'\1', docstring)

    return docstring
inspect.getdoc = _getdoc

def loadImage(imageFileName):
    import wx

    try:
        image = wx.Image(rootDir + os.sep + 'Images' + os.sep + imageFileName)
    except:
        image = None
    return image

def shapeClass(shapeName):
    import display.shape
    
    for shapeClass in display.shape.shapeClasses():
        if shapeClass.__name__ == shapeName:
            return shapeClass
    
    return None
    
library = None
config = None

enableNetworkMenu = ('DEBUG' in os.environ)

def scriptLocals():
    return {}

if __name__ == '__main__':
    
    from neuroptikon_app import NeuroptikonApp
    
    app = NeuroptikonApp(None)
    app.MainLoop()
    
