from networkx import *
from wx.py import dispatcher
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

try:
    import pydot
except:
    pydot = None


class Network:
    
    def __init__(self):
        self.graph = XGraph()
        self.objects = []
        self.idDict = {}   # TODO: weak ref dict?
        self.displays = []
    
    
    def findObject(self, objectClass, name = None):
        if name is not None:
            for object in self.objects:
                if isinstance(object, objectClass) and object.name == name:
                    return object
        return None
    
    
    def createRegion(self, addSubTerms = False, *args, **keywordArgs):
        region = Region(self, *args, **keywordArgs)
        self.addObject(region)
        
        if region.ontologyTerm is not None and addSubTerms:
            for term in region.ontologyTerm.parts:
                self.createRegion(ontologyTerm = term, parentRegion = region, addSubTerms = True)
        
        return region
    
    
    def findRegion(self, name = None):
        return self.findObject(Region, name)
    
    
    def regions(self):
        return self.objectsOfClass(Region)
    
    
    def createNeuron(self, *args, **keywordArgs):
        neuron = Neuron(self, *args, **keywordArgs)
        self.addObject(neuron)
        return neuron
    
    
    def findNeuron(self, name = None):
        return self.findObject(Neuron, name)
    
    
    def neurons(self):
        return self.objectsOfClass(Neuron)
    
    
    def createStimulus(self, *args, **keywordArgs):
        stimulus = Stimulus(self, *args, **keywordArgs)
        self.addObject(stimulus)
        return stimulus
    
    
    def findStimulus(self, name = None):
        return self.findObject(Stimulus, name)
    
    
    def stimuli(self):
        return self.objectsOfClass(Stimulus)
    
    
    def createMuscle(self, *args, **keywordArgs):
        muscle = Muscle(self, *args, **keywordArgs)
        self.addObject(muscle)
        return muscle
    
    
    def findMuscle(self, name = None):
        return self.findObject(Muscle, name)
    
    
    def muscles(self):
        return self.objectsOfClass(Muscle)
    
    
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
            self.graph.add_edge(id(object.terminus1.region), id(object.terminus2.region), object)
        elif isinstance(object, Innervation):
            self.graph.add_edge(id(object.neurite.neuron()), id(object.muscle), object)
        elif isinstance(object, Stimulus):
            self.graph.add_node(id(object))
            self.graph.add_edge(id(object), id(object.target), object)
        elif isinstance(object, Region) or isinstance(object, Neuron) or isinstance(object, Muscle):
            self.graph.add_node(id(object))
        dispatcher.send('addition', self, affectedObjects = [object])
    
    
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
        
        if pydot is None:
            return None
        
        if graph_attr is not None:
            graph_attributes = graph_attr
        else:
            graph_attributes = {}

        try:
            node_a = self.graph.node_attr
        except:
            node_a = {}
        if node_attr is not None:        
            node_a.update(node_attr)

        P = pydot.Dot(graph_type='graph', strict=False)

        for n in self.graph.nodes_iter():
            if n in node_a:
                attr=node_a[n]
            else:
                attr={}
            p=pydot.Node(str(n),**attr)
            P.add_node(p)
        
        # This is the workaround for the pydot bug.  As long as every edge has some attribute then it works.
        for (u, v, x) in self.graph.edges_iter():
            attr = {'label': ''}
            edge = pydot.Edge(str(u), str(v), **attr)
            P.add_edge(edge)

        try:
            P.obj_dict['attributes'].update(graph_attributes['graph'])
        except:
            pass
        try:
            P.obj_dict['nodes']['node'][0]['attributes'].update(graph_attributes['node'])
        except:
            pass
        try:
            P.obj_dict['nodes']['edge'][0]['attributes'].update(graph_attributes['edge'])
        except:
            pass

        return P
