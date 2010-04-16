#  Copyright (c) 2010 Howard Hughes Medical Institute.
#  All rights reserved.
#  Use is subject to Janelia Farm Research Campus Software Copyright 1.1 license terms.
#  http://license.janelia.org/license/jfrc_copyright_1_1.html

'''
Visualize any neurites that are not dedicated to a single connection, e.g. those created by the convenience methods like Neuron.synapseOn() or Neurite.arborize().

If nothing is selected then all neurites in the network will be visualized.  If there is a selection then only the neurites connected to the arborizations and synapses in the selection will be visualized.

This functionality will eventually be folded into Neuroptikon.

Warning: This script is currently incompatible with saving the network as display-only.  Duplicate neurites and branch points will get created when the display-only script is run.
'''


def visualizeNeurite(neurite):
    '''
    Visualize the indicated neurite and any neurites between it and the soma if they are not already visualized.
    
    Returns the visible proxy of the neurite that was created or that already existed.
    '''
    
    visibles = display.visiblesForObject(neurite)
    if any(visibles):
        return visibles[0]
    else:
        root = neurite.root
        if isinstance(root, Neuron):
            startVisible = display.visiblesForObject(root)[0]
        else:
            rootVisible = visualizeNeurite(root)
            startVisible = rootVisible.pathEndPoints()[1]
        neuriteVisible = display.visualizeObject(neurite)
        branchPointVisible = display.visualizeObject(None, opacity = 0.0, size = (0.005, 0.005, 0.005))
        neuriteVisible.setPathEndPoints(startVisible, branchPointVisible)
        # TODO: set the end point of everything else downstream of the branch point? 
        return neuriteVisible


def updateFlow(neuriteVisible, flowTo = False, flowFrom = False):
    '''
    Update the information flow back towards the neuron's soma.
    
    If a neurite has information flow then it is assumed that the flow travels all to the way to or from the soma.  This may not be biologically accurate in all cases.
    '''
    
    if flowTo:
        neuriteVisible.setFlowTo(True)
    if flowFrom:
        neuriteVisible.setFlowFrom(True)
    root = neuriteVisible.client.root
    if isinstance(root, Neurite):
        rootVisible = display.visiblesForObject(root)[0]
        updateFlow(rootVisible, flowTo = flowTo, flowFrom = flowFrom)


if any(display.selection()):
    arborizations = []
    synapses = []
    for object in display.selectedObjects():
        if isinstance(object, Arborization):
            arborizations += [object]
        elif isinstance(object, Synapse):
            synapses += [object]
else:
    arborizations = network.arborizations()
    synapses = network.synapses()

# Visualize any additional neurites between an arborization's neurite and its neuron.
for arborization in arborizations:
    root = arborization.neurite.root
    if not isinstance(root, Neuron):
        visibles = display.visiblesForObject(arborization)
        if any(visibles):
            arborizationPath = visibles[0]
            neuriteVisible = visualizeNeurite(arborization.neurite.root)
            if arborization.sendsOutput:
                updateFlow(neuriteVisible, flowTo = True)
            if arborization.receivesInput:
                updateFlow(neuriteVisible, flowFrom = True)
            arborizationPath.setPathEndPoints(neuriteVisible.pathEndPoints()[1], arborizationPath.pathEndPoints()[1])


# Visualize any additional neurites connecting to synapses.
for synapse in synapses:
    visibles = display.visiblesForObject(synapse)
    if any(visibles):
        synapsePath = visibles[0]
        synapseStart, synapseEnd = synapsePath.pathEndPoints()
        preRoot = synapse.preSynapticNeurite.root
        if not isinstance(preRoot, Neuron):
            preSynapticPath = visualizeNeurite(preRoot)
            updateFlow(preSynapticPath, flowTo = True)
            synapseStart = preSynapticPath.pathEndPoints()[1]
        postPartner = synapse.postSynapticPartners[0]
        if isinstance(postPartner, Neurite) and not isinstance(postPartner.root, Neuron):
            postSynapticPath = visualizeNeurite(postPartner.root)
            updateFlow(postSynapticPath, flowFrom = True)
            synapseEnd = postSynapticPath.pathEndPoints()[1]
        synapsePath.setPathEndPoints(synapseStart, synapseEnd)
        # TODO: handle synapses with multiple post-synaptic neurites


# TODO: gap junctions
# TODO: innervations
