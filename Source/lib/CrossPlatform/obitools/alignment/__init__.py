def columnIterator(alignment):
    lali = len(alignment[0])
    for p in xrange(lali):
        c = [x[p] for x in alignment]
        yield c