from obitools.ecopcr.taxonomy import Taxonomy


def addTaxonomyFilterOptions(optionManager):
    
    optionManager.add_option('--require-rank',
                             action="store", 
                             dest='requiredRank',
                             metavar="<RANK_NAME>",
                             type="string",
                             default=None,
                             help="select sequence with taxid tag containing "
                                  "a parent of rank <RANK_NAME>")
     
    optionManager.add_option('-t','--taxonomy',
                             action="store", dest="taxonomy",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR taxonomy Database "
                                  "name")

def taxonomyFilterGenerator(options):
    if options.taxonomy is not None:
        taxonomy = Taxonomy(options.taxonomy)
    
        def taxonomyFilter(seq):
            good = True
            if 'taxid' in seq:
                taxid = seq['taxid']
                if options.requiredRank is not None:
                    taxonatrank = taxonomy.getTaxonAtRank(taxid,options.requiredRank)
                    good = taxonatrank is not None
            
            return good
            
            
    else:
        def taxonomyFilter(seq):
            return True
 
    return taxonomyFilter
       
def taxonomyFilterIteratorGenerator(options):
    taxonomyFilter = taxonomyFilterGenerator(options)
    
    def filterIterator(seqiterator):
        for seq in seqiterator:
            if taxonomyFilter(seq):
                yield seq
                
    return filterIterator