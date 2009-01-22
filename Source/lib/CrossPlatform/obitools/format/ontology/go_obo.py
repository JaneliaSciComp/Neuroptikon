__docformat__ = 'restructuredtext'

import re
import string
import textwrap


from obitools.obo.go.parser import GOEntryIterator
from obitools.obo.go.parser import GOTerm
from obitools.obo.go.parser import GOEntry

"""
go_obo.py : gene_ontology_edit.obo  file parser:
----------------------------------------------------
  
- OBOFile class: open a flat file and return an entry.
            
"""
class OBOFile(object):
    """
        Iterator over all entries of an OBO file
    """
    
    def __init__(self,_path):
        self.file = GOEntryIterator(_path)
        
    def __iter__(self):
        return self

    def next(self):
        fiche = self.file.next()
        
        if isinstance(fiche, GOTerm):
            self.isaterm=True
            return Term(fiche)
        elif isinstance(fiche, GOEntry):
            self.isaterm=False
            return Entry(fiche)
        else:
            self.isaterm=False
            return Header(fiche)
          

############# tout le reste doit descendre a l'etage obitools/ogo/go/parser.py ##########

# define an XRef into a go_obo.py script in the microbi pylib
class Xref(object):
    """
    Class Xref
        Xref.db    Xref database
        Xref.id    Xref identifier
    """

    def __init__(self,description):
        data = description.split(':')
        self.db = data[0].strip()
        self.id = data[1].strip()

# define a RelatedTerm into a go_obo.py script in the microbi pylib
class RelatedTerm(object):
    """
    Class RelatedTerm
        RelatedTerm.relation    RelatedTerm relation
        RelatedTerm.related_term    RelatedTerm GO identifier
        RelatedTerm.comment    all terms have 0 or 1 comment
    """

    def __init__(self,relation,value,comment):
        self.relation = relation
        self.related_term = value.strip('GO:')
        self.comment = comment
        

# define into a go_obo.py script in the microbi pylib
#class Term(object):
#    """
#    class representing an OBO term (entry).
#    """
#
#    def __init__(self):
#      raise RuntimeError('biodb.go_obo is an abstract class')
#
#    def __checkEntry__(self):
#      minimum=(hasattr(self,'goid') )
#      if not minimum:
#        raise AssertionError('Misconstructed GO Term instance %s' % [x for x in dir(self) if x[0]!='_'])

class Term(object):
    """
    Class Term
        representing a GO term.
    """
    
    def __init__(self,data=None):
        """
        """
        self.data=data
        self.isaterm = True
        
        if data:
            self.__filtreGoid__()
            self.__filtreName__()
            self.__filtreComment__()
            self.__filtreSynonyms__()
            self.__filtreDef__()
            self.__filtreParents__()
            self.__filtreRelationships__()
            self.__filtreRelation__()
            self.__filtreObsolete__()
            self.__filtreAltIds__()
            self.__filtreXRefs__()
            self.__filtreSubsets__()
                
        # check if all required attributes were valued
        self.__checkEntry__()
    
    
    def __checkEntry__(self):
      minimum=(hasattr(self,'goid') )
      if not minimum:
        raise AssertionError('Misconstructed GO Term instance %s' % [x for x in dir(self) if x[0]!='_'])
    
        
    def __filtreGoid__(self):
        """
        Extract GO id.
        """
        self.goid = self.data.id.value.strip('GO:')

    def __filtreName__(self):
        """
        Extract GO name.
        """
        self.name = self.data.name.value

    def __filtreSynonyms__(self):
        """
        Extract GO synonym(s).
        """
        self.list_synonyms = {}
        if self.data.synonyms:
            for y in self.data.synonyms:
                self.list_synonyms[y.value] = y.scope
                
                
    def __filtreComment__(self):
        """
            manage None comments
        """
        if self.data.comment != None:
            self.comment = self.data.comment.value
        else:
            self.comment = ""
    
    def __filtreDef__(self):
        """
            Extract GO definition.
        """
        if self.data.definition != None:
            self.definition = self.data.definition.value
        else:
            self.definition = ""
                
    def __filtreParents__(self):
        """
            To make the is_a hierarchy
        """
        if self.data.is_a != None:
            self.is_a = set([isa.value.strip('GO:') for isa in self.data.is_a])
        else:
            self.is_a = set()    

    def __filtreRelation__(self):
        """
            To make the part_of hierarchy
        """
        self.part_of = set()
        self.regulates = set()
        self.negatively_regulates = set()
        self.positively_regulates = set()
        
        if self.data.relationship != None:
            for rel in self.data.relationship:
                if rel.relationship == "part_of":
                    self.part_of.add(rel.value.strip('GO:'))
                elif rel.relationship == "regulates":
                    self.regulates.add(rel.value.strip('GO:'))
                elif rel.relationship == "negatively_regulates":
                    self.negatively_regulates.add(rel.value.strip('GO:'))
                elif rel.relationship == "positively_regulates":
                    self.positively_regulates.add(rel.value.strip('GO:'))
        
        
    def __filtreRelationships__(self):
        """
            Relation list with other GO Terms (is_a, part_of or some regulates relation)
        """
        self.related_term =[]
        if self.data.relationship != None:
            for x in self.data.relationship:
                self.related_term.append(RelatedTerm(x.relationship,x.value,x.__doc__))
                #self.related_term.append(RelatedTerm(x.relationship,x.value,x.comment))
        if self.data.is_a != None:
            for x in self.data.is_a:
                self.related_term.append(RelatedTerm('is_a',x.value,x.__doc__))
                #self.related_term.append(RelatedTerm('is_a',x.value,x.comment))
                
                     
        
    def __filtreObsolete__(self):
        """
            for each obsolete terms corresponds a set of GO Identifiers
            so that this GO term is consider as others GO Terms
        """
        self.considers = set()
        self.replaces = set()
        self.is_obsolete = self.data.is_obsolete
        if self.data.is_obsolete:
            if self.data.consider:
                self.considers = set([considered.value.strip('GO:') for considered in self.data.consider])
            if self.data.replaced_by:
                self.replaces = set([replaced.value.strip('GO:') for replaced in self.data.replaced_by])
        
                
    def __filtreAltIds__(self):
        """
            alternate(s) id(s) for this term (= alias in the geneontology schema model!)
        """
        if self.data.alt_ids:
            self.alt_ids = set([x.value.strip('GO:') for x in self.data.alt_ids])
        else:
            self.alt_ids = set()
              
    def __filtreXRefs__(self):
        """
            cross references to other databases
        """
        self.xrefs = set()
        if self.data.xrefs:    
            self.xrefs = set([Xref(x.value.reference) for x in self.data.xrefs])
        
            
    def __filtreSubsets__(self):
        """
            subset label to make smaller sets of GO Terms
        """
        self.subsets = set()
        if self.data.subsets:
            self.subsets = set([x.value for x in self.data.subsets])
        
        
class Entry(object):
    """
        a Stanza entry, like [Typedef] for example
    """
    def __init__(self,data=None):
        self.data=data
        self.isaterm=False
        self.isanentry=True
    

class Header(object):
    """
        class representing a GO header.
    """
         
    def __init__(self,data=None):
        """
        """
        self.data=data
        self.isaterm = False
        
            

