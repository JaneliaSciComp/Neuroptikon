class ObjectList(list):
    
    def hasEqualAttrs(self, attributeName):
        value0 = getattr(self[0], attributeName)
        for object in self[1:]:
            if getattr(object, attributeName) != value0:
                return False
        return True
