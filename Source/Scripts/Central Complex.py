flyBrainOnt = library.ontology('flybrain')

regions={}

protocerebralBridge = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Protocerebral bridge'))
display.setVisiblePosition(protocerebralBridge, (0.0, 0.5, 0.0), True)
display.setVisibleSize(protocerebralBridge, (0.8, 0.05, 0.1))
display.setLabel(protocerebralBridge, '')
leftProtocerebralBridge = network.createRegion(name = 'Left protocerebral bridge', parentRegion = protocerebralBridge)
display.setLabel(leftProtocerebralBridge, '')
for i in range(8, 0, -1):
    regions['PB-L' + str(i)] = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(abbreviation= 'pcb' + str(i)), abbreviation = str(i), parentRegion = leftProtocerebralBridge)
rightProtocerebralBridge = network.createRegion(name = 'Right protocerebral bridge', parentRegion = protocerebralBridge)
display.setLabel(rightProtocerebralBridge, '')
for i in range(1, 9):
    regions['PB-R' + str(i)] = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(abbreviation = 'pcb' + str(i)), abbreviation = str(i), parentRegion = rightProtocerebralBridge)
display.setArrangedSpacing(protocerebralBridge, .005, recurse = True)

regions['DLPC-L'] = network.createRegion(name = 'DLPC-L', abbreviation = 'DLPC')
display.setVisiblePosition(regions['DLPC-L'], (0.83076923076923082, 0.46153846153846156, 0.0), True)
display.setVisibleSize(regions['DLPC-L'], (0.05, 0.08, 0.1))

fanShapedBody = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Fan-shaped body'))
display.setVisiblePosition(fanShapedBody, (0.0, 0.25, 0.0), True)
display.setVisibleSize(fanShapedBody, (0.55, 0.05, 0.1))
display.setLabel(fanShapedBody, '')
display.setArrangedSpacing(fanShapedBody, .005)
# TODO: how does this map to Arnim's latest ontology which has six FB layers?
for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
    regions['FB-' + letter] = network.createRegion(name = 'FB-' + letter, abbreviation = letter, parentRegion = fanShapedBody)

region = network.createRegion(name = 'DLPC-R', abbreviation = 'DLPC')
regions['DLPC-R'] = region
display.setVisiblePosition(region, (-0.89230769230769236, 0.46153846153846156, 0.0), True)
display.setVisibleSize(region, (0.05, 0.08, 0.1))

# TODO: how does this map to Arnim's latest ontology which has four EB rings?
ellipsoidBody = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Ellipsoid body'))
display.setVisiblePosition(ellipsoidBody, (0.0, -0.15, 0.0), True)
display.setVisibleSize(ellipsoidBody, (0.2, 0.35, 0.1))
display.setLabel(ellipsoidBody, '')
anteriorEB = network.createRegion(name = 'Anterior EB', parentRegion = ellipsoidBody)
regions['EB-ant-out'] = network.createRegion(name = 'Ellipsoid body anterior outer ring', abbreviation = 'outer ring', parentRegion = anteriorEB)
regions['EB-ant-in'] = network.createRegion(name = 'Ellipsoid body anterior inner ring', abbreviation = 'inner ring', parentRegion = anteriorEB)
posteriorEB = network.createRegion(name = 'Posterior EB', parentRegion = ellipsoidBody)
regions['EB-post-in'] = network.createRegion(name = 'Ellipsoid body posterior inner ring', abbreviation = 'inner ring', parentRegion = posteriorEB)
regions['EB-post-out'] = network.createRegion(name = 'Ellipsoid body posterior outer ring', abbreviation = 'outer ring', parentRegion = posteriorEB)
display.setArrangedAxis(ellipsoidBody, 'Y', recurse = True)

regions['LTR-L'] = network.createRegion(name = 'LTR-L', abbreviation = 'LTR')
display.setVisiblePosition(regions['LTR-L'], (0.81538461538461537, -0.076923076923076927, 0.0), True)
display.setVisibleSize(regions['LTR-L'], (0.07, 0.08, 0.1))

regions['LTR-R'] = network.createRegion(name = 'LTR-R', abbreviation = 'LTR')
display.setVisiblePosition(regions['LTR-R'], (-0.84615384615384615, -0.076923076923076927, 0.0), True)
display.setVisibleSize(regions['LTR-R'], (0.07, 0.08, 0.1))

region = network.createRegion(name = 'OF-L', abbreviation = 'OF')
regions['OF-L'] = region
display.setVisiblePosition(region, (0.81538461538461537, 0.19230769230769232, 0.0), True)
display.setVisibleSize(region, (0.07, 0.08, 0.1))

region = network.createRegion(name = 'OF-R', abbreviation = 'OF')
regions['OF-R'] = region
display.setVisiblePosition(region, (-0.84615384615384615, 0.19230769230769232, 0.0), True)
display.setVisibleSize(region, (0.07, 0.08, 0.1))

region = network.createRegion(name = 'VBO-L', abbreviation = 'VBO')
regions['VBO-L'] = region
display.setVisiblePosition(region, (0.7846153846153846, -0.33076923076923076, 0.0), True)
display.setVisibleSize(region, (0.1, 0.1, 0.1))

region = network.createRegion(name = 'VBO-R', abbreviation = 'VBO')
regions['VBO-R'] = region
display.setVisiblePosition(region, (-0.75384615384615383, -0.33076923076923076, 0.0), True)
display.setVisibleSize(region, (0.1, 0.1, 0.1))

noduli = network.createRegion(ontologyTerm = flyBrainOnt.findTerm(name = 'Noduli'))
display.setVisiblePosition(noduli, (0.0, -0.57692307692307687, 0.0), True)
display.setVisibleSize(noduli, (0.4, 0.06, 0.1))
display.setLabel(noduli, '')
leftNoduli = network.createRegion(name = 'Left noduli', parentRegion = noduli)
display.setLabel(leftNoduli, '')
display.setArrangedSpacing(leftNoduli, spacing = .005)
regions['N-L2'] = network.createRegion(name = 'N-L2', abbreviation = '2', parentRegion = leftNoduli)
regions['N-L1'] = network.createRegion(name = 'N-L1', abbreviation = '1', parentRegion = leftNoduli)
rightNoduli = network.createRegion(name = 'Right noduli', parentRegion = noduli)
display.setLabel(rightNoduli, '')
display.setArrangedSpacing(rightNoduli, spacing = .005)
regions['N-R1'] = network.createRegion(name = 'N-R1', abbreviation = '1', parentRegion = rightNoduli)
regions['N-R2'] = network.createRegion(name = 'N-R2', abbreviation = '2', parentRegion = rightNoduli)

neuron = network.createNeuron(name = 'pb-eb-ltr-L8', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-L8'], False, True)
neuron.arborize(regions['EB-post-in'], True, False)
neuron.arborize(regions['LTR-L'], True, False)

neuron = network.createNeuron(name = 'HFS-E2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L4'], False, True)
neuron.arborize(regions['FB-E'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'HFS-E1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R3'], False, True)
neuron.arborize(regions['FB-E'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'VFS-A1', abbreviation = 'VFS')
neuron.arborize(regions['PB-R8'], False, True)
neuron.arborize(regions['FB-A'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'eb-pb-vbo-aR4', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-R4'], True, False)
neuron.arborize(regions['EB-ant-out'], False, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'eb-pb-vbo-aR7', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-R7'], True, False)
neuron.arborize(regions['EB-post-out'], False, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'VFS-A2', abbreviation = 'VFS')
neuron.arborize(regions['PB-R7'], False, True)
neuron.arborize(regions['FB-A'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'VFS-E1', abbreviation = 'VFS')
neuron.arborize(regions['PB-L1'], False, True)
neuron.arborize(regions['FB-E'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'eb-pb-vbo-aR8', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-R8'], True, False)
neuron.arborize(regions['EB-ant-out'], False, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'pb-eb-ltr-L2', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-L2'], False, True)
neuron.arborize(regions['EB-ant-in'], True, False)
neuron.arborize(regions['LTR-L'], True, False)

neuron = network.createNeuron(name = 'VFS-E2', abbreviation = 'VFS')
neuron.arborize(regions['PB-L2'], False, True)
neuron.arborize(regions['FB-E'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'fan-1', abbreviation = 'fan')
neuron.arborize(regions['VBO-R'], False, True)
neuron.arborize(regions['FB-B'], True, True)
neuron.arborize(regions['N-R2'], True, True)

neuron = network.createNeuron(name = 'VFS-C2', abbreviation = 'VFS')
neuron.arborize(regions['PB-R3'], False, True)
neuron.arborize(regions['FB-C'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'VFS-C1', abbreviation = 'VFS')
neuron.arborize(regions['PB-R4'], False, True)
neuron.arborize(regions['FB-C'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'fan-2', abbreviation = 'fan')
neuron.arborize(regions['VBO-L'], False, True)
neuron.arborize(regions['FB-G'], True, True)
neuron.arborize(regions['N-L2'], True, True)

neuron = network.createNeuron(name = 'pb-eb-ltr-R2', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-R2'], False, True)
neuron.arborize(regions['EB-ant-in'], True, False)
neuron.arborize(regions['LTR-R'], True, False)

neuron = network.createNeuron(name = 'HFS-C1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R5'], False, True)
neuron.arborize(regions['FB-C'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'fb-no-1', abbreviation = 'fb-no')
neuron.arborize(regions['FB-A'], True, True)
neuron.arborize(regions['N-R2'], True, True)
neuron.arborize(regions['VBO-R'], False, True)

neuron = network.createNeuron(name = 'fb-no-2', abbreviation = 'fb-no')
neuron.arborize(regions['FB-H'], True, True)
neuron.arborize(regions['N-L2'], True, True)
neuron.arborize(regions['VBO-L'], False, True)

neuron = network.createNeuron(name = 'HFS-C2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L2'], False, True)
neuron.arborize(regions['FB-C'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'HFS-G1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R1'], False, True)
neuron.arborize(regions['FB-G'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'ltr-eb-R1-1', abbreviation = 'ltr-eb')
neuron.arborize(regions['LTR-L'], False, True)
neuron.arborize(regions['EB-post-in'], True, False)

neuron = network.createNeuron(name = 'ltr-eb-R1-2', abbreviation = 'ltr-eb')
neuron.arborize(regions['LTR-R'], False, True)
neuron.arborize(regions['EB-post-in'], True, False)

neuron = network.createNeuron(name = 'HFS-G2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L6'], False, True)
neuron.arborize(regions['FB-G'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'HFS-A2', abbreviation = 'HFS')
neuron.arborize(regions['PB-R7'], False, True)
neuron.arborize(regions['FB-A'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'HFS-A1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R8'], False, True)
neuron.arborize(regions['FB-A'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'eb-pb-vbo-aL3', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-L3'], True, False)
neuron.arborize(regions['EB-post-out'], False, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'eb-pb-vbo-aL7', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-L7'], True, False)
neuron.arborize(regions['EB-post-out'], False, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'pontine-ae-2', abbreviation = 'pontine')
neuron.arborize(regions['FB-A'], True, False)
neuron.arborize(regions['FB-E'], False, True)

neuron = network.createNeuron(name = 'pontine-ae-1', abbreviation = 'pontine')
neuron.arborize(regions['FB-A'], False, True)
neuron.arborize(regions['FB-E'], True, False)

neuron = network.createNeuron(name = 'eb-pb-vbo-aL4', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-L4'], True, False)
neuron.arborize(regions['EB-ant-out'], False, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'OF-L-1', abbreviation = 'OF')
neuron.arborize(regions['OF-L'], False, True)
neuron.arborize(regions['LTR-L'], True, False)

neuron = network.createNeuron(name = 'eb-pb-vbo-aL8', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-L8'], True, False)
neuron.arborize(regions['EB-ant-out'], False, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'VFS-F1', abbreviation = 'VFS')
neuron.arborize(regions['PB-L3'], False, True)
neuron.arborize(regions['FB-F'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'VFS-F2', abbreviation = 'VFS')
neuron.arborize(regions['PB-L4'], False, True)
neuron.arborize(regions['FB-F'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'VFS-H2', abbreviation = 'VFS')
neuron.arborize(regions['PB-L8'], False, True)
neuron.arborize(regions['FB-H'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'eb-pb-vbo-aR3', abbreviation = 'eb-pb-vbo')
neuron.arborize(regions['PB-R3'], True, False)
neuron.arborize(regions['EB-post-out'], False, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'VFS-H1', abbreviation = 'VFS')
neuron.arborize(regions['PB-L7'], False, True)
neuron.arborize(regions['FB-H'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'pontine-bf-1', abbreviation = 'pontine')
neuron.arborize(regions['FB-B'], False, True)
neuron.arborize(regions['FB-F'], True, False)

neuron = network.createNeuron(name = 'VFS-B1', abbreviation = 'VFS')
neuron.arborize(regions['PB-R6'], False, True)
neuron.arborize(regions['FB-B'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'VFS-B2', abbreviation = 'VFS')
neuron.arborize(regions['PB-R5'], False, True)
neuron.arborize(regions['FB-B'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'pontine-bf-2', abbreviation = 'pontine')
neuron.arborize(regions['FB-B'], True, False)
neuron.arborize(regions['FB-F'], False, True)

neuron = network.createNeuron(name = 'ltr-eb-R3-2', abbreviation = 'ltr-eb')
neuron.arborize(regions['LTR-R'], False, True)
neuron.arborize(regions['EB-ant-in'], True, False)

neuron = network.createNeuron(name = 'HFS-D1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R4'], False, True)
neuron.arborize(regions['FB-D'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'HFS-D2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L3'], False, True)
neuron.arborize(regions['FB-D'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'ltr-eb-R3-1', abbreviation = 'ltr-eb')
neuron.arborize(regions['LTR-L'], False, True)
neuron.arborize(regions['EB-ant-in'], True, False)

neuron = network.createNeuron(name = 'VFS-D2', abbreviation = 'VFS')
neuron.arborize(regions['PB-R1'], False, True)
neuron.arborize(regions['FB-D'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'HFS-H1', abbreviation = 'HFS')
neuron.arborize(regions['PB-L7'], False, True)
neuron.arborize(regions['FB-H'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'HFS-H2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L8'], False, True)
neuron.arborize(regions['FB-H'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'VFS-D1', abbreviation = 'VFS')
neuron.arborize(regions['PB-R2'], False, True)
neuron.arborize(regions['FB-D'], True, False)
neuron.arborize(regions['N-L1'], True, True)

neuron = network.createNeuron(name = 'fb-dlpc-1', abbreviation = 'fb-dlpc')
neuron.arborize(regions['FB-A'], True, True)
neuron.arborize(regions['DLPC-R'], False, True)

neuron = network.createNeuron(name = 'ltr-eb-R2-2', abbreviation = 'ltr-eb')
neuron.arborize(regions['LTR-R'], False, True)
neuron.arborize(regions['EB-ant-out'], True, False)

neuron = network.createNeuron(name = 'ltr-eb-R2-1', abbreviation = 'ltr-eb')
neuron.arborize(regions['LTR-L'], False, True)
neuron.arborize(regions['EB-ant-out'], True, False)

neuron = network.createNeuron(name = 'HFS-B2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L1'], False, True)
neuron.arborize(regions['FB-B'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'pb-eb-ltr-L6', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-L6'], False, True)
neuron.arborize(regions['EB-ant-in'], True, False)
neuron.arborize(regions['LTR-L'], True, False)

neuron = network.createNeuron(name = 'HFS-B1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R6'], False, True)
neuron.arborize(regions['FB-B'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'HFS-F2', abbreviation = 'HFS')
neuron.arborize(regions['PB-L5'], False, True)
neuron.arborize(regions['FB-F'], True, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'pb-eb-ltr-L4', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-L4'], False, True)
neuron.arborize(regions['EB-post-in'], True, False)
neuron.arborize(regions['LTR-L'], True, False)

neuron = network.createNeuron(name = 'HFS-F1', abbreviation = 'HFS')
neuron.arborize(regions['PB-R2'], False, True)
neuron.arborize(regions['FB-F'], True, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'pb-eb-ltr-R6', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-R6'], False, True)
neuron.arborize(regions['EB-ant-in'], True, False)
neuron.arborize(regions['LTR-R'], True, False)

neuron = network.createNeuron(name = 'pontine-cg-2', abbreviation = 'pontine')
neuron.arborize(regions['FB-C'], True, False)
neuron.arborize(regions['FB-G'], False, True)

neuron = network.createNeuron(name = 'pontine-cg-1', abbreviation = 'pontine')
neuron.arborize(regions['FB-C'], False, True)
neuron.arborize(regions['FB-G'], True, False)

neuron = network.createNeuron(name = 'fb-dlpc-2', abbreviation = 'fb-dlpc')
neuron.arborize(regions['FB-H'], True, True)
neuron.arborize(regions['DLPC-L'], False, True)

neuron = network.createNeuron(name = 'pontine-dh-2', abbreviation = 'pontine')
neuron.arborize(regions['FB-D'], True, False)
neuron.arborize(regions['FB-H'], False, True)

neuron = network.createNeuron(name = 'pb-eb-ltr-R8', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-R8'], False, True)
neuron.arborize(regions['EB-post-in'], True, False)
neuron.arborize(regions['LTR-R'], True, False)

neuron = network.createNeuron(name = 'VFS-G2', abbreviation = 'VFS')
neuron.arborize(regions['PB-L6'], False, True)
neuron.arborize(regions['FB-G'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'VFS-G1', abbreviation = 'VFS')
neuron.arborize(regions['PB-L5'], False, True)
neuron.arborize(regions['FB-G'], True, False)
neuron.arborize(regions['N-R1'], True, True)

neuron = network.createNeuron(name = 'vbo-vbo-1', abbreviation = 'vbo-vbo')
neuron.arborize(regions['VBO-L'], False, True)
neuron.arborize(regions['VBO-R'], True, False)

neuron = network.createNeuron(name = 'pontine-dh-1', abbreviation = 'pontine')
neuron.arborize(regions['FB-D'], False, True)
neuron.arborize(regions['FB-H'], True, False)

neuron = network.createNeuron(name = 'OF-R-1', abbreviation = 'OF')
neuron.arborize(regions['OF-R'], False, True)
neuron.arborize(regions['LTR-R'], True, False)

neuron = network.createNeuron(name = 'vbo-vbo-2', abbreviation = 'vbo-vbo')
neuron.arborize(regions['VBO-R'], False, True)
neuron.arborize(regions['VBO-L'], True, False)

neuron = network.createNeuron(name = 'pb-eb-ltr-R4', abbreviation = 'pb-eb-ltr')
neuron.arborize(regions['PB-R4'], False, True)
neuron.arborize(regions['EB-post-in'], True, False)
neuron.arborize(regions['LTR-R'], True, False)

display.autoLayout()
display.setUseGhosts(True)
