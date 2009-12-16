#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

# TODO: is there a way to globally inject haveEqualAttr() into the standard list class?  Then this class wouldn't be needed.

class ObjectList(list):
    
    def haveEqualAttr(self, attributePath):
        if not any(self):
            return False
        if '.' in attributePath:
            (subObjectAttribute, attributeName) = attributePath.split('.')
            object = getattr(self[0], subObjectAttribute)
        else:
            subObjectAttribute = None
            attributeName = attributePath
            object = self[0]
        value0 = getattr(object, attributeName)
        isMethod = type(value0) == type(self.haveEqualAttr)
        if isMethod:
            value0 = value0()
        for object in self[1:]:
            if subObjectAttribute is not None:
                object = getattr(object, subObjectAttribute)
            value = getattr(object, attributeName)
            if isMethod:
                value = value()
            if value != value0:
                return False
        return True
