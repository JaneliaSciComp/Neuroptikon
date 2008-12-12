neuron1 = network.createNeuron('Neuron 1')
neuron2 = network.createNeuron('Neuron 2')
lightStimulus = network.createStimulus(neuron1, "light")
smellStimulus = network.createStimulus(neuron2, "smell")
regionA = network.createRegion('Region A')
regionB = network.createRegion('Region B')
pathway = regionA.addPathwayToRegion(regionB)
neuron1.arborize(regionA, True, False)
neuron1.arborize(regionB, True, False)
neuron2.arborize(regionA, True, False)
neuron2.arborize(regionB, True, False)
neuron1.synapseOn(neuron2)
neuron3 = network.createNeuron('Neuron 3')
neuron3.arborize(regionA, False, True)
neuron3.arborize(regionB, False, True)
muscle = network.createMuscle('Muscle X')
neuron3.innervate(muscle)

display.autoLayout("graphviz")
display.centerView()
