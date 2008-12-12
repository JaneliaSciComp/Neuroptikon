from networkx import *
from pydispatch import dispatcher
from Region import Region
from Pathway import Pathway
from Neuron import Neuron
from Neurite import Neurite
from Arborization import Arborization
from Synapse import Synapse
from GapJunction import GapJunction
from Stimulus import Stimulus
from Muscle import Muscle
from Innervation import Innervation
import pydot


class Network:
    
    def __init__(self):
        self.graph = XGraph()
        self.displayFilters = []
        self.objects = []
        self.idDict = {}   # TODO: weak ref dict?
        self.displays = []
    
    
    def createRegion(self, name=None):
        region = Region(self, name)
        self.addObject(region)
        return region
    
    
    def createNeuron(self, name=None):
        neuron = Neuron(self, name)
        self.addObject(neuron)
        return neuron
    
    
    def createStimulus(self, target, type="light"):
        if type == "smell":
            stimulus = Stimulus(self, target, Stimulus.SMELL)
        elif type == "taste":
            stimulus = Stimulus(self, target, Stimulus.TASTE)
        elif type == "sound":
            stimulus = Stimulus(self, target, Stimulus.SOUND)
        else:
            stimulus = Stimulus(self, target, Stimulus.LIGHT)
        self.addObject(stimulus)
        return stimulus
    
    
    def createMuscle(self, name=None):
        muscle = Muscle(self, name)
        self.addObject(muscle)
        return muscle
    
    
    def addObject(self, object):
        self.objects.append(object)
        self.idDict[id(object)] = object
        if isinstance(object, Arborization):
            self.graph.add_edge(id(object.neurite.neuron()), id(object.region), object)
        elif isinstance(object, Synapse):
            self.graph.add_edge(id(object.presynapticNeurite.neuron()), id(object.postsynapticNeurites[0].neuron()), object) # TODO: need to handle hyper-edges?
        elif isinstance(object, GapJunction):
            neurites = list(object.neurites)
            self.graph.add_edge(id(neurites[0].neuron()), id(neurites[1].neuron()), object)
        elif isinstance(object, Pathway):
            regions = list(object.regions)
            self.graph.add_edge(id(regions[0]), id(regions[1]), object)
        elif isinstance(object, Innervation):
            self.graph.add_edge(id(object.neurite.neuron()), id(object.muscle), object)
        elif isinstance(object, Stimulus):
            self.graph.add_node(id(object))
            self.graph.add_edge(id(object), id(object.target), object)
        elif isinstance(object, Region) or isinstance(object, Neuron) or isinstance(object, Muscle):
            self.graph.add_node(id(object))
        dispatcher.send("addition", self, [object])
    
    
    def objectWithId(self, node):
        return self.idDict[node]
    
    
    def objectsOfClass(self, objectClass):
        objects = []
        for object in self.objects:
            if isinstance(object, objectClass):
                objects.append(object)
        return objects
    
    
    def addDisplay(self, display):
        self.displays.append(display)
    
    
    def removeDisplay(self, display):
        self.displays.remove(display)


    def to_pydot(self, graph_attr=None, node_attr=None, edge_attr=None):
        # This is a custom version of networkx.drawing.nx_pydot.to_pydot() that works around a bug in pydot 1.0.2.
        
        if graph_attr is not None:            graph_attributes = graph_attr
        else:            graph_attributes = {}        try:            node_a = self.graph.node_attr        except:            node_a = {}        if node_attr is not None:                    node_a.update(node_attr)        P = pydot.Dot(graph_type='graph', strict=False)        for n in self.graph.nodes_iter():            if n in node_a:                attr=node_a[n]            else:                attr={}            p=pydot.Node(str(n),**attr)            P.add_node(p)        
        # This is the workaround for the pydot bug.  As long as every edge has some attribute then it works.        for (u, v, x) in self.graph.edges_iter():            attr = {'label': ''}            edge = pydot.Edge(str(u), str(v), **attr)            P.add_edge(edge)        try:            P.obj_dict['attributes'].update(graph_attributes['graph'])        except:            pass        try:            P.obj_dict['nodes']['node'][0]['attributes'].update(graph_attributes['node'])        except:            pass        try:            P.obj_dict['nodes']['edge'][0]['attributes'].update(graph_attributes['edge'])        except:            pass        return P
