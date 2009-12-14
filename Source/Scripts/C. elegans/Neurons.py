"""
This script creates all of the neurons in the C. elegans nervous system and their interconnections.

 Dataset from:
   L. R. Varshney, B. L. Chen, E. Paniagua, D. H. Hall, and D. B. Chklovskii, "Structural properties of the Caenorhabditis elegans neuronal network," 2009, in preparation.
"""

spanTypes = {'S': 'sort', 'L': 'long'}
ambiguityCodes = {'MB': 'cell body position ambiguous', 'MTS': 'tail synapses ambiguous and/or sparse connections in the tail', 'MAS': 'anterior body ambiguous and/or sparse connections in the anterior', 'MD': 'dorsal side ambiguous', 'MAD': 'anterior and dorsal side ambiguous', 'MS': 'neurons with sublateral processes not covered by reconstructions', 'RDI': 'dorsal reconstruction incomplete', 'RDM': 'dorsal reconstruction completely missing', 'RVI': 'ventral reconstruction incomplete'}
AY_GanglionGroups = {'A': 'anterior ganglion', 'B': 'dorsal ganglion', 'C': 'lateral ganglion', 'D': 'ventral ganglion', 'E': 'retrovesicular ganglion', 'F': 'posterolateral ganglion', 'G': 'ventral cord neuron group', 'H': 'pre-anal ganglion', 'J': 'dorsorectal ganglion', 'K': 'lumbar ganglion'}

neurons = {}

# Load the neurons from the Neurons.txt file.
neuronTypesFile = open('Neurons.txt')
try:
    for line in neuronTypesFile:
        if line[0] != '#':
            fields = line.split('\t')
            
            neuron = network.createNeuron(name = fields[0])
            neurons[neuron.name] = neuron
            
            # Determine the side ('L'eft, 'R'ight or 'U') from the last character of the name.
            if neuron.name.endswith('L'):
                neuron.addAttribute('Side', Attribute.STRING_TYPE, 'L')
            elif neuron.name.endswith('R'):
                neuron.addAttribute('Side', Attribute.STRING_TYPE, 'R')
            else:
                neuron.addAttribute('Side', Attribute.STRING_TYPE, 'U')
            
            neuron.addAttribute('Soma A-P Position', Attribute.DECIMAL_TYPE, float(fields[1]))
            
            neuron.addAttribute('Span', Attribute.STRING_TYPE, spanTypes[fields[3]])
            
            # Add any ambiguity code and type.
            ambiguityCode = fields[4]
            if ambiguityCode != '':
                neuron.addAttribute('Ambiguity Code', Attribute.STRING_TYPE, ambiguityCode)
                if ambiguityCode in ambiguityCodes:
                    neuron.addAttribute('Ambiguity Type', Attribute.STRING_TYPE, ambiguityCodes[ambiguityCode])
            
            # Add any ganglion group as defined by Achacoso and Yamamoto W.S., 1992.
            ganglionGroup = AY_GanglionGroups.get(fields[14], None)
            if ganglionGroup:
                neuron.addAttribute('AY Ganglion Group', Attribute.STRING_TYPE, ganglionGroup)
            
            # Add the numeric identifier specified in Achacoso and Yamamoto W.S., 1992.
            neuron.addAttribute('AY Number', Attribute.INTEGER_TYPE, int(fields[15]))
            
            # Add functions.
            functions = fields[16]
            if 'S' in functions:
                neuron.setHasFunction(Neuron.Function.SENSORY, True)
            if 'I' in functions:
                neuron.setHasFunction(Neuron.Function.INTERNEURON, True)
            if 'M' in functions:
                neuron.setHasFunction(Neuron.Function.MOTOR, True)
            
            # Add neurotransmitters.
            neurotransmitters = fields[17]
            for ntName in neurotransmitters.split(','):
                ntName = ntName.strip()
                if ntName != '':
                    nt = library.neurotransmitter(ntName)
                    if nt:
                        neuron.neurotransmitters += [nt]
                    else:
                        print 'Unknown neurotransmitter: ' + ntName
finally:
    neuronTypesFile.close()

    
# Load the chemical synapses from an adjacency matrix in the Chemical.txt file.
# It is assumed that the first line of the file indicates the neuron name for each column (and thus for each row as well).
synapseFile = open('Chemical.txt')
try:
    neuronNames = synapseFile.next().strip().split('\t')
    for preNeuron, synapseCounts in map(None, neuronNames, synapseFile):
        for postNeuron, synapseCount in map(None, neuronNames, synapseCounts.strip().split('\t')):
            if synapseCount.strip() != '0':
                neurons[preNeuron.strip()].synapseOn(neurons[postNeuron.strip()]).addAttribute('Count', Attribute.INTEGER_TYPE, int(synapseCount.strip()))
finally:
    synapseFile.close()

    
# Load the gap junctions from an adjacency matrix in the Gap Junction.txt file.
# It is assumed that the first line of the file indicates the neuron name for each column (and thus for each row as well).
gapJunctionFile = open('Gap Junction.txt')
try:
    neuronNames = gapJunctionFile.next().strip().split('\t')
    count = 0
    for neuron1, gapJunctionCounts in map(None, neuronNames, gapJunctionFile):
        for neuron2, gapJunctionCount in map(None, neuronNames[count:], gapJunctionCounts.strip().split('\t')[count:]):
            if gapJunctionCount.strip() != '0':
                neurons[neuron1.strip()].gapJunctionWith(neurons[neuron2.strip()]).addAttribute('Count', Attribute.INTEGER_TYPE, int(gapJunctionCount.strip()))
        count += 1
finally:
    gapJunctionFile.close()
