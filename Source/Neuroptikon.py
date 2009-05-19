import os, platform, stat, sys

if 'OSG_NOTIFY_LEVEL' not in os.environ:
    os.environ['OSG_NOTIFY_LEVEL'] = 'ALWAYS'

if hasattr(sys, "frozen"):
    rootDir = os.path.dirname(sys.executable)
    if platform.system() == 'Darwin':
        rootDir = os.path.dirname(rootDir) + os.sep + 'Resources'
    platformLibPath = rootDir
else:
    rootDir = os.path.abspath(os.path.dirname(sys.modules['__main__'].__file__))
    
    
    
    # Make sure that the library paths are set up correctly for the current location.
    commonLibPath = rootDir + os.sep + 'lib' + os.sep + 'CrossPlatform'
    platformLibPath = rootDir + os.sep + 'lib' + os.sep + platform.system()

    if platform.system() == 'Darwin':
        # Use the copy of wx in /Library
        import wxversion
        wxversion.select('2.8')
        
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

# Make sure all the graphviz pieces can be found and used.
try:
    fdpPath = platformLibPath + os.sep + 'fdp'
    if os.access(fdpPath, os.F_OK):
        # Make sure graphviz's binaries can find the graphviz plug-ins.
        os.environ['GVBINDIR'] = platformLibPath + os.sep + 'graphviz'

        # Make sure our custom build of graphviz's binaries can be found.
        os.environ['PATH'] = platformLibPath + os.pathsep + os.environ['PATH']

        # Make sure fdp is executable.
        if os.stat(fdpPath).st_mode & stat.S_IXUSR == 0:
            os.chmod(fdpPath, os.stat(fdpPath).st_mode | stat.S_IXUSR)
except:
    (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
    print 'Could not configure graphviz (' + exceptionValue.message + ')'
    
# Set up for internationalization.
import gettext as gettext_module, __builtin__
__builtin__.gettext = gettext_module.translation('Neuroptikon', fallback = True).lgettext

import wx
import wx.lib.mixins.inspection
from wx import py
import xml.etree.ElementTree as ElementTree
from NeuroptikonFrame import NeuroptikonFrame
from Network.Network import Network
from Network.Neuron import Neuron
from Network.Attribute import Attribute
from Library.Library import Library
from Library.Neurotransmitter import Neurotransmitter
from Library.NeuronClass import NeuronClass
from Library.Modality import Modality
from Library.Ontology import Ontology
from Library.Texture import Texture
from Preferences import Preferences
import Inspectors
from Inspection.InspectorFrame import InspectorFrame
import osg


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
            
            self.rootDir = rootDir
            
            self.library = Library()
            self._loadDefaultLibraryItems()
            
            self._networks = []
            
            self.preferences = Preferences()
            self.inspector = InspectorFrame()
            
            # Keep track of open frames so we can close them on quit.
            # TODO: use wxWidget's document/view framework instead
            self._frames = [self.preferences, self.inspector]
            self.SetExitOnFrameDelete(False)
            
            osg.DisplaySettings.instance().setNumMultiSamples(4);
            
            # open an empty network by default
            # TODO: pref to re-open last doc?
            self.onNewNetwork()
            
            return True
        
        
        def _loadDefaultLibraryItems(self):
            self.library.add(Neurotransmitter('ACh', gettext('Acetylcholine')))
            self.library.add(Neurotransmitter('DA', gettext('Dopamine')))
            self.library.add(Neurotransmitter('epinephrine', gettext('Epinephrine')))
            self.library.add(Neurotransmitter('GABA', gettext('Gamma-aminobutyric acid'), gettext('GABA')))
            self.library.add(Neurotransmitter('GLU', gettext('Glutamate')))
            self.library.add(Neurotransmitter('glycine', gettext('Glycine')))
            self.library.add(Neurotransmitter('histamine', gettext('Histamine')))
            self.library.add(Neurotransmitter('norepinephrine', gettext('Norepinephrine')))
            self.library.add(Neurotransmitter('5-HT', gettext('Serotonin')))
            
            self.library.add(NeuronClass(identifier = 'basket', name = gettext('Basket cell'), polarity = Neuron.Polarity.MULTIPOLAR, function = Neuron.Function.INTERNEURON, activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('GABA')]))
            self.library.add(NeuronClass(identifier = 'pyramidal', name = gettext('Pyramidal cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'excitatory', neurotransmitters = [self.library.neurotransmitter('glutamate')]))
            self.library.add(NeuronClass(identifier = 'RSad pyramidal', name = gettext('RSad Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'RSna pyramidal', name = gettext('RSna Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'IB pyramidal', name = gettext('IB Pyramidal cell'), parentClass = self.library.neuronClass('pyramidal')))
            self.library.add(NeuronClass(identifier = 'betz', name = gettext('Betz cell'), parentClass = self.library.neuronClass('pyramidal'), function = Neuron.Function.MOTOR))
            self.library.add(NeuronClass(identifier = 'medium spiny', name = gettext('Medium spiny neuron'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('GABA')]))
            self.library.add(NeuronClass(identifier = 'purkinje', name = gettext('Purkinje cell'), polarity = Neuron.Polarity.MULTIPOLAR, activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('GABA')]))
            self.library.add(NeuronClass(identifier = 'renshaw', name = gettext('Renshaw cell'), polarity = Neuron.Polarity.MULTIPOLAR, function = Neuron.Function.INTERNEURON, activation = 'inhibitory', neurotransmitters = [self.library.neurotransmitter('glycine')]))
            self.library.add(NeuronClass(identifier = 'anterior horn', name = gettext('Anterior horn cell')))
            
            self.library.add(Modality('light', gettext('Light')))
            self.library.add(Modality('odor', gettext('Odor')))
            self.library.add(Modality('sound', gettext('Sound')))
            self.library.add(Modality('taste', gettext('Taste')))
            
            # Load any ontologies in <root>/Ontologies
            try:
                for fileName in os.listdir(rootDir + os.sep + 'Ontologies'):
                    if fileName != '.svn':
                        identifier = os.path.splitext(fileName)[0]
                        ontology = Ontology(identifier)
                        try:
                            ontology.importOBO(rootDir + os.sep + 'Ontologies' + os.sep + fileName)
                            self.library.add(ontology)
                        except:
                            (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                            print 'Could not import ontology ' + fileName + ' (' + exceptionValue.message + ')'
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                print 'Could not import ontologies (' + exceptionValue.message + ')'
            
            # Load any textures in <root>/Textures
            try:
                for fileName in os.listdir(rootDir + os.sep + 'Textures'):
                    if fileName != '.svn':
                        identifier = os.path.splitext(fileName)[0]
                        texture = Texture(identifier, gettext(identifier))
                        if texture.loadImage(rootDir + os.sep + 'Textures' + os.sep + fileName):
                            self.library.add(texture)
            except:
                (exceptionType, exceptionValue, exceptionTraceback) = sys.exc_info()
                print 'Could not import textures (' + exceptionValue.message + ')'
        
        
        def onQuit(self, event):
            ok2Quit = True
            for frame in self._frames:
                if not frame.Close():
                    ok2Quit = False
            if ok2Quit:
                self.ExitMainLoop()
        
        
        def loadImage(self, imageFileName):
            try:
                image = wx.Image(self.rootDir + os.sep + 'Images' + os.sep + imageFileName)
            except:
                image = None
            return image
        
        
        def scriptLocals(self):
            return {'createNetwork': self.createNetwork, 
                    'displayNetwork': self.displayNetwork, 
                    'networks': self.networks, 
                    'library': self.library, 
                    'Neurotransmitter': Neurotransmitter, 
                    'Modality': Modality, 
                    'Ontology': Ontology, 
                    'NeuralPolarity': Neuron.Polarity, 
                    'NeuralFunction': Neuron.Function, 
                    'Attribute': Attribute}
        
        
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
            self._console.Raise()
        
        
        def onNewNetwork(self, event=None):
            network = self.createNetwork()
            self.displayNetwork(network)
        
        
        def createNetwork(self):
            network = Network()
            self._networks.append(network)
            #TODO: implement doc/view framework
            return network
        
        
        def onOpenNetwork(self, event):
            dlg = wx.FileDialog(None, gettext('Choose a saved network to open:'), '', '', '*.xml', wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                try:
                    xmlTree = ElementTree.parse(path)
                    
                    # Instantiate the network
                    networkElement = xmlTree.find('Network')
                    network = Network.fromXMLElement(networkElement)
                    if network is None:
                        raise ValueError, gettext('Could not load the network')
                    network.savePath = path
                    self._networks.append(network)
                    
                    # Instantiate any displays
                    for frameElement in xmlTree.findall('DisplayWindow'):
                        frame = NeuroptikonFrame.fromXMLElement(frameElement, network = network)
                        if frame is None:
                            raise ValueError, gettext('Could not create one of the displays')
                        frame.Show(True)
                        frame.Raise()
                        self._frames.append(frame)
                    
                    # Create a default display if none were specified in the file.
                    if len(network.displays) == 0:
                        self.displayNetwork(network)
                except:
                    raise
        
        
        def networks(self):
            return self._networks
        
        
        def displayNetwork(self, network):
            frame = NeuroptikonFrame(network = network)
            frame.Show(True)
            frame.Raise()
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
            self.preferences.Raise()
            return self.preferences
        
        
        def onBrowseLibrary(self, event):
            self.library.browse()
        
        
        def onOpenInspector(self, event):
            self.inspector.Show(True)
            self.inspector.Raise()
            return self.inspector
        
        
        def onOpenWxinspector(self, event):
            self.ShowInspectionTool()
            
    
    def run():
        app = Neuroptikon(None)
        app.MainLoop()
    
    run( )
    
