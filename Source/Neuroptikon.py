import os, platform, stat, sys

# Make sure that the library paths are set up correctly for the current location.
commonLibPath = os.getcwd() + os.sep + 'lib' + os.sep + 'CrossPlatform'
platformLibPath = os.getcwd() + os.sep + 'lib' + os.sep + platform.system()

if platform.system() == 'Darwin':
    libraryEnvVar = 'DYLD_LIBRARY_PATH'
elif platform.system() == 'Windows':
    libraryEnvVar = 'PATH'
#elif platform.system() == 'Linux':
#    libraryEnvVar = 'LD_LIBRARY_PATH'

if libraryEnvVar not in os.environ or platformLibPath not in os.environ[libraryEnvVar].split(os.pathsep):
    # Add the search path for the native libraries to the enviroment.
    if libraryEnvVar in os.environ:
        os.environ[libraryEnvVar] = platformLibPath + os.pathsep + os.environ[libraryEnvVar]
    else:
        os.environ[libraryEnvVar] = platformLibPath
    # Restart this script with the same instance of python and the same arguments.
    arguments = [sys.executable]
    arguments.extend(sys.argv)
    os.system(' '.join(arguments))
    raise SystemExit

sys.path.insert(0, commonLibPath)
sys.path.insert(0, platformLibPath)

fdpPath = platformLibPath + os.sep + 'fdp'
if os.access(fdpPath, os.F_OK):
    # Make sure graphviz's binaries can find the graphviz plug-ins.
    os.environ['GVBINDIR'] = platformLibPath + os.sep + 'graphviz'

    # Make sure our custom build of graphviz's binaries can be found.
    os.environ['PATH'] = platformLibPath + os.pathsep + os.environ['PATH']

    # Make sure fdp is executable.
    os.chmod(fdpPath, os.stat(fdpPath).st_mode | stat.S_IXUSR)

# Set up for internationalization.
import gettext as gettext_module, __builtin__
__builtin__.gettext = gettext_module.translation('Neuroptikon', fallback = True).lgettext

import wx
import wx.lib.mixins.inspection
from wx import py
from NeuroptikonFrame import NeuroptikonFrame
from Network.Network import Network
from Network.Neuron import Neuron
from Library.Library import Library
from Library.Neurotransmitter import Neurotransmitter
from Library.NeuronClass import NeuronClass
from Library.Modality import Modality
from Library.Ontology import Ontology
from Preferences import Preferences
from Inspection.InspectorFrame import InspectorFrame


def debugException(type, value, tb):
    import traceback; traceback.print_tb(tb)
    print "Exception:", value
    import pdb; pdb.pm()


if __name__ == "__main__":
    #if __debug__:
    #    sys.excepthook = debugException
    
    class Neuroptikon(wx.lib.mixins.inspection.InspectableApp):
        
        def OnInit(self):
            
            #self.convertRealData(None)
            
            self.library = Library()
            self._loadDefaultLibraryItems()
            
            self._networks = []
            
            self.preferences = Preferences()
            self.inspector = InspectorFrame()
            
            # Keep track of open frames so we can close them on quit.
            # TODO: use wxWidget's document/view framework instead
            self._frames = [self.preferences, self.inspector]
            self.SetExitOnFrameDelete(False)
            
            # open an empty network by default
            # TODO: pref to re-open last doc?
            self.onNewNetwork()
            
            return True
        
        
        def _loadDefaultLibraryItems(self):
            self.library.add(Neurotransmitter('acetylcholine', gettext('Acetylcholine')))
            self.library.add(Neurotransmitter('dopamine', gettext('Dopamine')))
            self.library.add(Neurotransmitter('epinephrine', gettext('Epinephrine')))
            self.library.add(Neurotransmitter('GABA', gettext('Gamma-aminobutyric acid'), gettext('GABA')))
            self.library.add(Neurotransmitter('glutamate', gettext('Glutamate')))
            self.library.add(Neurotransmitter('glycine', gettext('Glycine')))
            self.library.add(Neurotransmitter('histamine', gettext('Histamine')))
            self.library.add(Neurotransmitter('norepinephrine', gettext('Norepinephrine')))
            self.library.add(Neurotransmitter('serotonin', gettext('Serotonin')))
            
            self.library.add(NeuronClass(identifier = 'basket', name = gettext('Basket cell'), polarity = Neuron.Polarity.MULTIPOLAR, function = Neuron.Function.INTERNEURON, excitatory = False, neurotransmitter = self.library.neurotransmitter('GABA')))
            self.library.add(NeuronClass(identifier = 'pyramidal', name = gettext('Pyramidal cell'), polarity = Neuron.Polarity.MULTIPOLAR, excitatory = True, neurotransmitter = self.library.neurotransmitter('glutamate')))
            self.library.add(NeuronClass(identifier = 'RSad pyramidal', name = gettext('RSad Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'RSna pyramidal', name = gettext('RSna Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'IB pyramidal', name = gettext('IB Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'betz', name = gettext('Betz cell'), parentClass = self.library.neuronClass('pyramidal'), function = Neuron.Function.MOTOR))
            self.library.add(NeuronClass(identifier = 'medium spiny', name = gettext('Medium spiny neuron'), polarity = Neuron.Polarity.MULTIPOLAR, excitatory = False, neurotransmitter = self.library.neurotransmitter('GABA')))
            self.library.add(NeuronClass(identifier = 'purkinje', name = gettext('Purkinje cell'), polarity = Neuron.Polarity.MULTIPOLAR, excitatory = False, neurotransmitter = self.library.neurotransmitter('GABA')))
            self.library.add(NeuronClass(identifier = 'renshaw', name = gettext('Renshaw cell'), polarity = Neuron.Polarity.MULTIPOLAR, function = Neuron.Function.INTERNEURON, excitatory = False, neurotransmitter = self.library.neurotransmitter('glycine')))
            self.library.add(NeuronClass(identifier = 'anterior horn', name = gettext('Anterior horn cell')))
            
            self.library.add(Modality('light', gettext('Light')))
            self.library.add(Modality('odor', gettext('Odor')))
            self.library.add(Modality('sound', gettext('Sound')))
            self.library.add(Modality('taste', gettext('Taste')))
            
            flyOntology = Ontology('drosophila brain', name = gettext('Drosophila brain'))
            flyOntology.importOBO('Library/flybrain.obo')
            self.library.add(flyOntology)

        
        
        def onQuit(self, event):
            ok2Quit = True
            for frame in self._frames:
                if not frame.Close():
                    ok2Quit = False
            if ok2Quit:
                self.ExitMainLoop()
        
        
        def scriptLocals(self):
            return {'createNetwork': self.createNetwork, 
                    'displayNetwork': self.displayNetwork, 
                    'networks': self.networks, 
                    'library': self.library, 
                    'Neurotransmitter': Neurotransmitter, 
                    'Modality': Modality, 
                    'Ontology': Ontology, 
                    'NeuralPolarity': Neuron.Polarity, 
                    'NeuralFunction': Neuron.Function}
        
        
        def onRunScript(self, event):
            dlg = wx.FileDialog(None, gettext('Choose a script to run'), 'Scripts', '', '*.py', wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    execfile(dlg.GetPath(), self.scriptLocals())
                except:
                    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                    dialog = wx.MessageDialog(self, exceptionValue.message, gettext('An error occurred at line %d of the script:') % exceptionTraceback.tb_next.tb_lineno, style = wx.ICON_ERROR | wx.OK)
                    dialog.ShowModal()
            dlg.Destroy()
        
        
        def onOpenConsole(self, event):
            if '_console' not in dir(self):
                confDir = wx.StandardPaths.Get().GetUserDataDir()
                if not os.path.exists(confDir):
                    os.mkdir(confDir)
                fileName = os.path.join(confDir, 'Console.config')
                self.config = wx.FileConfig(localFilename=fileName)
                self.config.SetRecordDefaults(True)
                self._console = py.shell.ShellFrame(title=gettext('Console'), config=self.config, dataDir=confDir, locals=self.scriptLocals())
                #TODO: need to just hide the console window on close or set up some kind of callback to clear _console when the console closes
            self._console.Show()
        
        
        def onNewNetwork(self, event=None):
            network = self.createNetwork()
            self.displayNetwork(network)
        
        
        def createNetwork(self):
            network = Network()
            self._networks.append(network)
            #TODO: implement doc/view framework
            return network
        
        
        def networks(self):
            return self._networks
        
        
        def displayNetwork(self, network):
            frame = NeuroptikonFrame(None)
            frame.display.setNetwork(network)
            frame.Show(True)
            self._frames.append(frame)
            return frame.display
        
        
        def convertRealData(self, display):
            """ Convert the data from the 0.87 prototype to a script """
            text = 'regions={}\n\n'
            from realdata import realdata 
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
        
        
        def onOpenPreferences(self, event):
            self.preferences.Show(True)
            return self.preferences
        
        
        def onBrowseLibrary(self, event):
            self.library.browse()
        
        
        def onOpenInspector(self, event):
            self.inspector.Show(True)
            return self.inspector
        
        
        def onOpenWxinspector(self, event):
            self.ShowInspectionTool()
            
    
    def run():
        app = Neuroptikon(None)
        app.MainLoop()
    
    run( )
    
