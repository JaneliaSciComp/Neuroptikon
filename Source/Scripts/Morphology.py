'''
Two examples of neural morphology.

2. A neuron is created with three levels of branching.
'''

def example1():
    '''
    Create a neuron with a single process that branches multiple times to form two separate arbors and then synapses onto a second neuron.
    '''
    
    neuron1 = network.createNeuron(name = '1')
    neuron2 = network.createNeuron(name = '2')
    regionA = network.createRegion(name = 'A')
    regionB = network.createRegion(name = 'B')
    
    # Create the root of the process.
    neurite1 = neuron1.extendNeurite()
    
    # The process first branches to arborize region A.
    neurite2 = neurite1.extendNeurite()
    neurite2.arborize(regionA, sendsOutput = True)
    neurite3 = neurite1.extendNeurite()
    
    # The process then branches again to arborize region B.
    neurite4 = neurite3.extendNeurite()
    neurite4.arborize(regionB, sendsOutput = True)
    
    # The process branches a final time and synapses on the second neuron.
    neurite5 = neurite3.extendNeurite()
    neurite5.synapseOn(neuron2)


def example2():
    '''
    Create a neuron with three levels of branching, each level getting "bushier".  Each final branch synapses onto another neuron. 
    '''
    import random
    
    # Create the central body.
    neuronX = network.createNeuron(name = 'X')
    
    # Extend neurites from each of the "leaves" of the current tree.
    leaves = [neuronX]
    for branchLevel in range(3):
        oldLeaves = list(leaves)
        leaves = []
        for leaf in oldLeaves:
            for branch in range(2 * (branchLevel + 1)):
                leaves += [leaf.extendNeurite()]
    
    # Create the final synapses.
    for leaf in leaves:
        if random.choice((True, False)):
            leaf.synapseOn(network.createNeuron())
        else:
            network.createNeuron().synapseOn(leaf)

# Build the examples
example1()
example2()

# By default the morphology of the process is not shown, the arborizations and synapse in the visualization will connect directly to the neuron's soma.
# The 'Show Neurites' scripts exposes the morphology.
execfile('Show Neurites.py')

# Layout the examples (using graphviz if it's available).
try:
    display.performLayout(layouts['Graphviz'])
except:
    display.performLayout() # fall back to the default
    
# Now layout the whole mess and make the flow look better than the defaults.
display.setDefaultFlowSpacing(0.02)
display.setDefaultFlowSpeed(0.02)
display.setShowNeuronNames(True)
