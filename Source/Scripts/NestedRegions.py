flyBrainOnt = library.ontology('flybrain')

# Build the network

ellipsoidBody = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Ellipsoid body'))
anteriorEB = network.createRegion(name = 'Anterior EB', parentRegion = ellipsoidBody)
anteriorEBInnerRing = network.createRegion(name = 'Anterior EB inner ring', abbreviation = 'Inner ring', parentRegion = anteriorEB)
anteriorEBOuterRing = network.createRegion(name = 'Anterior EB outer ring', abbreviation = 'Outer ring', parentRegion = anteriorEB)
posteriorEB = network.createRegion(name = 'Posterior EB', parentRegion = ellipsoidBody)
posteriorEBInnerRing = network.createRegion(name = 'Posterior EB inner ring', abbreviation = 'Inner ring', parentRegion = posteriorEB)
posteriorEBOuterRing = network.createRegion(name = 'Posterior EB outer ring', abbreviation = 'Outer ring', parentRegion = posteriorEB)

vln = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Ventrolateral Neuropils'))

neuron1 = network.createNeuron()
neuron1.arborize(vln)
neuron1.arborize(posteriorEBInnerRing)

neuron2 = network.createNeuron()
neuron2.arborize(anteriorEBInnerRing)
neuron2.arborize(vln)


# Set up the display

display.setVisibleSize(ellipsoidBody, (0.1, 0.2, 0.1))
display.setViewDimensions(3)
display.autoLayout()
