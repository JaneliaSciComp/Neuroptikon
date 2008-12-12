import urllib, xlrd

# Download the data from wormatlas
urlHandle = urllib.urlopen("http://www.wormatlas.org/handbook/fig.s/NeuronConnect.xls")
book = xlrd.open_workbook(file_contents=urlHandle.read())
sheet = book.sheet_by_index(0)

neurons = {}
for rowNum in range(1, sheet.nrows):
    neuron1_name = str(sheet.cell_value(rowx=rowNum, colx=0).upper())
    neuron2_name = str(sheet.cell_value(rowx=rowNum, colx=1).upper())
    type = sheet.cell_value(rowx=rowNum, colx=2).upper()
    count = int(sheet.cell_value(rowx=rowNum, colx=3))
    if type.startswith("S"):
        if neuron1_name in neurons:
            neuron1 = neurons[neuron1_name]
        else:
            neuron1 = network.createNeuron(neuron1_name)
            neurons[neuron1_name] = neuron1
        if neuron2_name in neurons:
            neuron2 = neurons[neuron2_name]
        else:
            neuron2 = network.createNeuron(neuron2_name)
            neurons[neuron2_name] = neuron2
        alreadyExists = False
        for synapse in neuron1.outgoingSynapses(): 
            if synapse.postsynapticNeurites[0].neuron == neuron2:
                alreadyExists = True
        if not alreadyExists:
            synapse = neuron1.synapseOn(neuron2)
            for j in range(count - 1):
                synapse.presynapticNeurite.synapseOn(synapse.postsynapticNeurites[0])
    elif type == "EJ" and neuron1_name < neuron2_name:
        if neuron1_name in neurons:
            neuron1 = neurons[neuron1_name]
        else:
            neuron1 = network.createNeuron(neuron1_name)
            neurons[neuron1_name] = neuron1
        if neuron2_name in neurons:
            neuron2 = neurons[neuron2_name]
        else:
            neuron2 = network.createNeuron(neuron2_name)
            neurons[neuron2_name] = neuron2
        alreadyExists = False
        for gapJunction in neuron1.gapJunctions():
            if gapJunction.neurites == set([neuron1, neuron2]):
                alreadyExists = True
        if not alreadyExists:
            gapJunction = neuron1.gapJunctionWith(neuron2)
            for j in range(count - 1):
                neurites = list(gapJunction.neurites)
                neurites[0].gapJunctionWith(neurites[1])

display.setViewDimensions(3)
display.autoLayout("spectral-mitya")
display.centerView()
