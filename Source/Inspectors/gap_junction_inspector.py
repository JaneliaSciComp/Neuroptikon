#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import wx
from object_inspector import ObjectInspector
from network.gap_junction import GapJunction


class GapJunctionInspector( ObjectInspector ):
    
    @classmethod
    def objectClass(cls):
        return GapJunction
