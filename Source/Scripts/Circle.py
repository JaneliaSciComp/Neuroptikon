count = 8
neurons = {}
for i in range(count):
    neurons[i] = network.createNeuron(name = str(i))
for i in range(count):
    for j in range(count):
        if i < j:
            neurons[i].synapseOn(neurons[j])

display.autoLayout()
