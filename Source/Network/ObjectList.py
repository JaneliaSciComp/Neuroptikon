# TODO: is there a way to globally inject haveEqualAttr() into the standard list class?  Then this class wouldn't be needed.

class ObjectList(list):
    
    def haveEqualAttr(self, attributeName):
        value0 = getattr(self[0], attributeName)
        isMethod = type(value0) == type(self.haveEqualAttr)
        if isMethod:
            value0 = value0()
        for object in self[1:]:
            value = getattr(object, attributeName)
            if isMethod:
                value = value()
            if value != value0:
                return False
        return True
