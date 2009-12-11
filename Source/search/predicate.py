class Predicate(object):
    def __init__(self, statement=lambda x: False, *args, **keywords):
        object.__init__(self, *args, **keywords)
        self.statement = statement
    
    def matches(self, object):
        return self.statement(object)


class CompoundPredicate(object):
    def __init__(self, *args, **keywords):
        object.__init__(self, *args, **keywords)
        self.predicates = []
        self.matchAll = True
    
    def addStatement(self, statement):
        self.predicates.append(Predicate(statement))
    
    def matches(self, object):
        if self.matchAll:
            for predicate in self.predicates:
                if not predicate.matches(object):
                    return False
            return True
        else:
            for predicate in self.predicates:
                if predicate.matches(object):
                    return True
            return False
