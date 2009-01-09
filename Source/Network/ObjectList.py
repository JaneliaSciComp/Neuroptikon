# TODO: is there a way to globally inject haveEqualAttr() into the standard list class?  Then this class wouldn't be needed.

class ObjectList(list):
    
    def haveEqualAttr(self, attributeName):
        value0 = getattr(self[0], attributeName)
        for object in self[1:]:
            if getattr(object, attributeName) != value0:
                return False
        return True
