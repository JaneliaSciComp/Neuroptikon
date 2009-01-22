
def uniqSequence(seqIterator,taxonomy=None):    
    uniques={}
    uniqSeq=[]
    
    for seq in seqIterator:    
        s = str(seq)
        if s in uniques:
            s = uniques[s]
            if 'count' in seq:
                s['count']+=seq['count']
            else:
                s['count']+=1
            if taxonomy is not None and 'taxid' in seq:
                s['merged_taxid'].add(seq['taxid'])
            s['merged'].append(seq.id)
        else:
            uniques[s]=seq
            if 'count' not in seq:
                seq['count']=1
            if taxonomy is not None:
                seq['merged_taxid']=set([])
                if 'taxid' in seq:
                    seq['merged_taxid'].add(seq['taxid'])
            seq['merged']=[seq.id]
            uniqSeq.append(seq)

    if taxonomy is not None:
        for seq in uniqSeq:
            if seq['merged_taxid']:
                seq['taxid']=taxonomy.lastCommonTaxon(*list(seq['merged_taxid']))
                tsp = taxonomy.getSpecies(seq['taxid'])
                tgn = taxonomy.getGenus(seq['taxid'])
                tfa = taxonomy.getFamily(seq['taxid'])
                
                if tsp is not None:
                    sp_sn = taxonomy.getScientificName(tsp)
                else:
                    sp_sn="###"
                    tsp=-1
                    
                if tgn is not None:
                    gn_sn = taxonomy.getScientificName(tgn)
                else:
                    gn_sn="###"
                    tgn=-1
                    
                if tfa is not None:
                    fa_sn = taxonomy.getScientificName(tfa)
                else:
                    fa_sn="###"
                    tfa=-1
                    
                seq['species']=tsp
                seq['genus']=tgn
                seq['family']=tfa
                    
                seq['species_sn']=sp_sn
                seq['genus_sn']=gn_sn
                seq['family_sn']=fa_sn
                
                seq['rank']=taxonomy.getRank(seq['taxid'])
                seq['scientific_name']=fa_sn = taxonomy.getScientificName(seq['taxid'])
                
                    
                     

    return uniqSeq

def _cmpOnKeyGenerator(key,reverse=False):
    def compare(x,y):
        try:
            c1 = x[key]
        except KeyError:
            c1=None
            
        try:
            c2 = y[key]
        except KeyError:
            c2=None
            
        if reverse:
            s=c1
            c1=c2
            c2=s
        return cmp(c1,c2)
    
    return compare

def sortSequence(seqIterator,key,reverse=False):
    seqs = list(seqIterator)
    seqs.sort(_cmpOnKeyGenerator(key, reverse))
    return seqs
    