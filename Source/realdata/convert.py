import realdata

if __name__ == "__main__":
    """ Convert the data from the 0.87 prototype to a script """
    text = 'regions={}\n\n'
    for regionName in sorted(realdata.regions):
        props = realdata.regions[regionName]
        label = props[0]
        text += "regions['%s'] = network.createRegion(name = '%s', abbreviation = '%s')\n" % (regionName, regionName, label)
        x, y, width, height = props[1][1]
        position = ((x + width / 2.0 - 50.0) / 650.0, ((350.0 - y) + height / 2.0) / 650.0, 0.0)
        size = (width / 650.0, height / 650.0, 0.01)
        text += "display.setVisiblePosition(regions['%s'], %s, True)\ndisplay.setVisibleSize(regions['%s'], %s)\n\n" % (regionName, position, regionName, size)
    for neuronName in realdata.connections:
        props = realdata.connections[neuronName]
        label = props[0]
        text += "neuron = network.createNeuron(name = '%s', abbreviation = '%s')\n" % (neuronName, label)
        nodeList = props[1]
        for node in nodeList:
            iob = node[0]
            if iob == 'o' or iob == 'b':
                sendsOutput = 'True'
            else:
                sendsOutput = 'False'
            if iob == 'i' or iob == 'b':
                receivesInput = 'True'
            else:
                receivesInput = 'False'
            text += "neuron.arborize(regions['%s'], %s, %s)\n" % (node[1], sendsOutput, receivesInput)
        text += '\n'
    # TODO: region groups
    text += 'display.autoLayout("graphviz")\ndisplay.centerView()\n'
    print text
