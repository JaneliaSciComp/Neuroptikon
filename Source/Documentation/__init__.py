""" Documentation package """

__version__ = "1.0.0"

import neuroptikon

import wx
import os.path, sys, urllib

_sharedFrame = None


def baseURL():
    if neuroptikon.runningFromSource:
        basePath = os.path.join(neuroptikon.rootDir, 'Documentation', 'build', 'Documentation')
    else:
        basePath = os.path.join(neuroptikon.rootDir, 'Documentation')
    
    return 'file:' + urllib.pathname2url(basePath) + '/'


def showPage(page):
    pageURL = baseURL() + page

    # Try to open an embedded WebKit-based help browser. 
    try:
        import documentation_frame
        documentation_frame.showPage(pageURL)
    except:
        raise
        # Fall back to using the user's default browser outside of Neuroptikon.
        #wx.LaunchDefaultBrowser(pageURL)
