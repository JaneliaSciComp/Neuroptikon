#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

import neuroptikon
import wx
from library_item import LibraryItem
from ontology_term import OntologyTerm
from ontology_frame import OntologyFrame
import obitools.obo.parser as obo


# Term ID mapping from previous 'flybrain' ontology to new 'Drosophila adult' ontology.
# This is used to do automatic conversion of XML docs saved with references to the old ontology.
# TODO: remove before external release along  with __contains__, __getitem__ and get methods below.
GMR_JFRC_map = {'GMR:10000238': 'JFRC:0000001754', 'GMR:10000128': 'JFRC:0000001625', 'GMR:10000201': 'JFRC:0000001870', 'GMR:10000200': 'JFRC:0000001939', 'GMR:10000203': 'JFRC:0000001927', 'GMR:10000202': 'JFRC:0000001746', 'GMR:10000232': 'JFRC:0000001645', 'GMR:10000209': 'JFRC:0000001935', 'GMR:10000172': 'JFRC:0000001900', 'GMR:10000078': 'JFRC:0000001672', 'GMR:10000079': 'JFRC:0000001690', 'GMR:10000176': 'JFRC:0000001563', 'GMR:10000175': 'JFRC:0000001902', 'GMR:10000147': 'JFRC:0000001888', 'GMR:10000072': 'JFRC:0000001766', 'GMR:10000111': 'JFRC:0000001665', 'GMR:10000070': 'JFRC:0000001768', 'GMR:10000071': 'JFRC:0000001764', 'GMR:10000076': 'JFRC:0000001866', 'GMR:10000077': 'JFRC:0000001739', 'GMR:10000075': 'JFRC:0000001743', 'GMR:10000182': 'JFRC:0000001781', 'GMR:10000188': 'JFRC:0000001921', 'GMR:10000261': 'JFRC:0000001639', 'GMR:10000129': 'JFRC:0000001627', 'GMR:10000239': 'JFRC:0000001771', 'GMR:10000260': 'JFRC:0000001637', 'GMR:10000181': 'JFRC:0000001779', 'GMR:10000148': 'JFRC:0000001892', 'GMR:10000149': 'JFRC:0000001890', 'GMR:10000146': 'JFRC:0000001884', 'GMR:10000119': 'JFRC:0000001565', 'GMR:10000144': 'JFRC:0000001599', 'GMR:10000145': 'JFRC:0000001601', 'GMR:10000142': 'JFRC:0000001593', 'GMR:10000143': 'JFRC:0000001595', 'GMR:10000140': 'JFRC:0000001589', 'GMR:10000118': 'JFRC:0000001741', 'GMR:10000065': 'JFRC:0000001784', 'GMR:10000230': 'JFRC:0000001609', 'GMR:10000067': 'JFRC:0000001868', 'GMR:10000066': 'JFRC:0000001798', 'GMR:10000061': 'JFRC:0000001878', 'GMR:10000060': 'JFRC:0000001856', 'GMR:10000063': 'JFRC:0000001659', 'GMR:10000062': 'JFRC:0000001657', 'GMR:10000069': 'JFRC:0000001737', 'GMR:10000068': 'JFRC:0000001773', 'GMR:10000189': 'JFRC:0000001895', 'GMR:10000234': 'JFRC:0000001674', 'GMR:10000235': 'JFRC:0000001726', 'GMR:10000098': 'JFRC:0000001704', 'GMR:10000099': 'JFRC:0000001706', 'GMR:10000236': 'JFRC:0000001728', 'GMR:10000090': 'JFRC:0000001688', 'GMR:10000092': 'JFRC:0000001718', 'GMR:10000093': 'JFRC:0000001720', 'GMR:10000094': 'JFRC:0000001722', 'GMR:10000095': 'JFRC:0000001724', 'GMR:10000096': 'JFRC:0000001700', 'GMR:10000097': 'JFRC:0000001702', 'GMR:10000151': 'JFRC:0000001899', 'GMR:10000150': 'JFRC:0000001872', 'GMR:10000152': 'JFRC:0000001904', 'GMR:10000155': 'JFRC:0000001912', 'GMR:10000154': 'JFRC:0000001910', 'GMR:10000157': 'JFRC:0000001948', 'GMR:10000156': 'JFRC:0000001914', 'GMR:10000010': 'JFRC:0000001805', 'GMR:10000011': 'JFRC:0000001806', 'GMR:10000012': 'JFRC:0000001807', 'GMR:10000013': 'JFRC:0000001808', 'GMR:10000014': 'JFRC:0000001809', 'GMR:10000015': 'JFRC:0000001811', 'GMR:10000016': 'JFRC:0000001812', 'GMR:10000017': 'JFRC:0000001813', 'GMR:10000018': 'JFRC:0000001814', 'GMR:10000019': 'JFRC:0000001815', 'GMR:10000233': 'JFRC:0000001647', 'GMR:10000089': 'JFRC:0000001686', 'GMR:10000088': 'JFRC:0000001684', 'GMR:10000083': 'JFRC:0000001698', 'GMR:10000082': 'JFRC:0000001696', 'GMR:10000081': 'JFRC:0000001694', 'GMR:10000080': 'JFRC:0000001692', 'GMR:10000087': 'JFRC:0000001682', 'GMR:10000086': 'JFRC:0000001680', 'GMR:10000085': 'JFRC:0000001678', 'GMR:10000084': 'JFRC:0000001676', 'GMR:10000110': 'JFRC:0000001670', 'GMR:10000141': 'JFRC:0000001591', 'GMR:10000240': 'JFRC:0000001777', 'GMR:10000003': 'JFRC:0000001555', 'GMR:10000002': 'JFRC:0000001553', 'GMR:10000001': 'JFRC:0000001551', 'GMR:10000007': 'JFRC:0000001801', 'GMR:10000006': 'JFRC:0000001876', 'GMR:10000005': 'JFRC:0000001750', 'GMR:10000004': 'JFRC:0000001557', 'GMR:10000124': 'JFRC:0000001617', 'GMR:10000125': 'JFRC:0000001619', 'GMR:10000009': 'JFRC:0000001804', 'GMR:10000008': 'JFRC:0000001803', 'GMR:10000120': 'JFRC:0000001571', 'GMR:10000121': 'JFRC:0000001611', 'GMR:10000122': 'JFRC:0000001613', 'GMR:10000123': 'JFRC:0000001615', 'GMR:10000246': 'JFRC:0000001874', 'GMR:10000263': 'JFRC:0000001794', 'GMR:10000241': 'JFRC:0000001786', 'GMR:10000231': 'JFRC:0000001643', 'GMR:10000243': 'JFRC:0000001859', 'GMR:10000242': 'JFRC:0000001789', 'GMR:10000249': 'JFRC:0000001733', 'GMR:10000248': 'JFRC:0000001882', 'GMR:10000038': 'JFRC:0000001834', 'GMR:10000039': 'JFRC:0000001835', 'GMR:10000036': 'JFRC:0000001832', 'GMR:10000037': 'JFRC:0000001833', 'GMR:10000034': 'JFRC:0000001830', 'GMR:10000035': 'JFRC:0000001831', 'GMR:10000032': 'JFRC:0000001828', 'GMR:10000033': 'JFRC:0000001829', 'GMR:10000030': 'JFRC:0000001826', 'GMR:10000031': 'JFRC:0000001827', 'GMR:10000170': 'JFRC:0000001923', 'GMR:10000139': 'JFRC:0000001587', 'GMR:10000138': 'JFRC:0000001585', 'GMR:10000137': 'JFRC:0000001603', 'GMR:10000136': 'JFRC:0000001583', 'GMR:10000135': 'JFRC:0000001579', 'GMR:10000132': 'JFRC:0000001633', 'GMR:10000131': 'JFRC:0000001631', 'GMR:10000130': 'JFRC:0000001629', 'GMR:10000257': 'JFRC:0000001940', 'GMR:10000174': 'JFRC:0000001929', 'GMR:10000215': 'JFRC:0000001668', 'GMR:10000179': 'JFRC:0000001937', 'GMR:10000245': 'JFRC:0000001863', 'GMR:10000029': 'JFRC:0000001825', 'GMR:10000028': 'JFRC:0000001824', 'GMR:10000180': 'JFRC:0000001761', 'GMR:10000178': 'JFRC:0000001567', 'GMR:10000187': 'JFRC:0000001925', 'GMR:10000184': 'JFRC:0000001886', 'GMR:10000185': 'JFRC:0000001944', 'GMR:10000021': 'JFRC:0000001817', 'GMR:10000020': 'JFRC:0000001816', 'GMR:10000023': 'JFRC:0000001819', 'GMR:10000022': 'JFRC:0000001818', 'GMR:10000025': 'JFRC:0000001821', 'GMR:10000024': 'JFRC:0000001820', 'GMR:10000027': 'JFRC:0000001823', 'GMR:10000026': 'JFRC:0000001822', 'GMR:10000108': 'JFRC:0000001661', 'GMR:10000109': 'JFRC:0000001656', 'GMR:10000102': 'JFRC:0000001712', 'GMR:10000103': 'JFRC:0000001714', 'GMR:10000100': 'JFRC:0000001708', 'GMR:10000101': 'JFRC:0000001710', 'GMR:10000106': 'JFRC:0000001756', 'GMR:10000107': 'JFRC:0000001635', 'GMR:10000104': 'JFRC:0000001716', 'GMR:10000105': 'JFRC:0000001731', 'GMR:10000250': 'JFRC:0000001894', 'GMR:10000199': 'JFRC:0000001857', 'GMR:10000194': 'JFRC:0000001906', 'GMR:10000197': 'JFRC:0000001758', 'GMR:10000247': 'JFRC:0000001880', 'GMR:10000191': 'JFRC:0000001597', 'GMR:10000193': 'JFRC:0000001775', 'GMR:10000192': 'JFRC:0000001581', 'GMR:10000252': 'JFRC:0000001897', 'GMR:10000229': 'JFRC:0000001607', 'GMR:10000228': 'JFRC:0000001577', 'GMR:10000221': 'JFRC:0000001752', 'GMR:10000227': 'JFRC:0000001575', 'GMR:10000226': 'JFRC:0000001573', 'GMR:10000225': 'JFRC:0000001569', 'GMR:10000224': 'JFRC:0000001559', 'GMR:10000115': 'JFRC:0000001649', 'GMR:10000114': 'JFRC:0000001651', 'GMR:10000117': 'JFRC:0000001561', 'GMR:10000058': 'JFRC:0000001854', 'GMR:10000059': 'JFRC:0000001855', 'GMR:10000113': 'JFRC:0000001671', 'GMR:10000112': 'JFRC:0000001641', 'GMR:10000054': 'JFRC:0000001850', 'GMR:10000055': 'JFRC:0000001851', 'GMR:10000056': 'JFRC:0000001852', 'GMR:10000057': 'JFRC:0000001853', 'GMR:10000050': 'JFRC:0000001846', 'GMR:10000051': 'JFRC:0000001847', 'GMR:10000052': 'JFRC:0000001848', 'GMR:10000053': 'JFRC:0000001849', 'GMR:10000262': 'JFRC:0000001792', 'GMR:10000237': 'JFRC:0000001735', 'GMR:10000166': 'JFRC:0000001946', 'GMR:10000167': 'JFRC:0000001917', 'GMR:10000168': 'JFRC:0000001919', 'GMR:10000126': 'JFRC:0000001621', 'GMR:10000216': 'JFRC:0000001605', 'GMR:10000217': 'JFRC:0000001933', 'GMR:10000214': 'JFRC:0000001666', 'GMR:10000127': 'JFRC:0000001623', 'GMR:10000212': 'JFRC:0000001653', 'GMR:10000213': 'JFRC:0000001662', 'GMR:10000210': 'JFRC:0000001931', 'GMR:10000244': 'JFRC:0000001861', 'GMR:10000258': 'JFRC:0000001942', 'GMR:10000163': 'JFRC:0000001908', 'GMR:10000164': 'JFRC:0000001748', 'GMR:10000165': 'JFRC:0000001796', 'GMR:10000049': 'JFRC:0000001845', 'GMR:10000048': 'JFRC:0000001844', 'GMR:10000047': 'JFRC:0000001843', 'GMR:10000046': 'JFRC:0000001842', 'GMR:10000045': 'JFRC:0000001841', 'GMR:10000044': 'JFRC:0000001840', 'GMR:10000043': 'JFRC:0000001839', 'GMR:10000042': 'JFRC:0000001838', 'GMR:10000041': 'JFRC:0000001837', 'GMR:10000040': 'JFRC:0000001836'}


class Ontology(LibraryItem, dict):
    
    @classmethod
    def displayName(cls):
        return gettext('Ontology')
    
    
    @classmethod
    def listProperty(cls):
        return 'ontologies'
    
    
    @classmethod
    def lookupProperty(cls):
        return 'ontology'
    
    
    @classmethod
    def bitmap(cls):
        bitmap = None
        try:
            image = neuroptikon.loadImage("Ontology.png")
            if image is not None and image.IsOk():
                bitmap = wx.BitmapFromImage(image)
        except:
            pass
        return bitmap
    
    
    @classmethod
    def frameClass(cls):
        return OntologyFrame
    
    
    def __init__(self, identifier = None, *args, **keywordArgs):
        LibraryItem.__init__(self, identifier, *args, **keywordArgs)
        self.rootTerms = []
        self.name = identifier
        
        if identifier == 'Drosophila adult':
            self.synonyms += ['flybrain']
    
    
    def __repr__(self):
        return 'Ontology \'%s\' (%d roots)' % (self.name, len(self.rootTerms))
    
    
    def __contains__(self, key):
        return dict.__contains__(self, key) or (self.identifier == 'Drosophila adult' and key in GMR_JFRC_map)
    
    
    def __getitem__(self, key):
        if self.identifier == 'Drosophila adult' and key.startswith('GMR'):
            jfrcKey = GMR_JFRC_map[key]
            if dict.__contains__(self, jfrcKey):
                return dict.__getitem__(self, jfrcKey)
            else:
                raise KeyError
        else:
            return dict.__getitem__(self, key)
    
    
    def get(self, key, default = None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
            
    
    def importOBO(self, filePath):
        unresolvedRefs = []
        for entry in obo.OBOEntryIterator(open(filePath)):
            if entry.isHeader:
                if 'name' in entry and len(entry['name']) > 0 and len(entry['name'][0].value) > 0:
                    self.name = entry['name'][0].value
            elif entry.stanzaName == 'Term':
                term = OntologyTerm(self, oboStanza = entry)
                self[term.identifier] = term
                
                if term.partOf is None:
                    self.rootTerms.append(term)
                elif not isinstance(term.partOf, OntologyTerm):
                    unresolvedRefs.append(term)
        
        # Set the parent of any terms that came before their parent in the file.
        for term in unresolvedRefs:
            if term.partOf not in self:
                self.rootTerms = []
                self.clear()
                raise ValueError, gettext('The parent (%s) of term "%s" (%s) is not in the ontology.') % (term.partOf, term.name, term.identifier)
            parent = self[term.partOf]
            term.partOf = parent
            parent.parts.append(term)
    
    
    def findTerm(self, name = None, abbreviation = None):
        matchingTerm = None
        
        for term in self.itervalues():
            if (name is not None and name.upper() == term.name.upper()) or \
               (abbreviation is not None and term.abbreviation is not None and abbreviation.upper() == term.abbreviation.upper()):
                matchingTerm = term
                break
        
        return matchingTerm
    
    
    def findTerms(self, namePart = None, abbreviationPart = None):
        matchingTerms = []
        
        for term in self.itervalues():
            if (namePart is not None and term.name is not None and term.name.upper().find(namePart.upper()) != -1) or \
               (abbreviationPart is not None and term.abbreviation is not None and term.abbreviation.upper().find(abbreviationPart.upper()) != -1):
                matchingTerms.append(term)
        
        return matchingTerms
    
