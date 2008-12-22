import os, platform, sys

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

# Make sure graphviz's binaries can find the graphviz plug-ins.
os.environ['GVBINDIR'] = platformLibPath + os.sep + 'graphviz'

# Make sure our custom build of graphviz's binaries can be found.
os.environ['PATH'] = platformLibPath + os.pathsep + os.environ['PATH']

import wx
import wx.lib.mixins.inspection
from NeuroptikonFrame import NeuroptikonFrame
from Network.Network import Network
from Inspector import Inspector

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
            
            self._networks = []
            
            self.inspector = Inspector(None)
            
            # Keep track of open frames so we can close them on quit.
            # TODO: use wxWidget's document/view framework instead
            self._frames = [self.inspector]
            self.SetExitOnFrameDelete(False)
            
            # open an empty network by default
            # TODO: pref to re-open last doc?
            self.onNewNetwork()
            
            return True
        
        
        def onQuit(self, event):
            ok2Quit = True
            for frame in self._frames:
                if not frame.Close():
                    ok2Quit = False
            if ok2Quit:
                self.ExitMainLoop()
        
        
        def onRunScript(self, event):
            dlg = wx.FileDialog(None, 'Choose a script to run', 'Scripts', '', '*.py', wx.OPEN)  # TODO: make this portable
            if dlg.ShowModal() == wx.ID_OK:
                locals = {"createNetwork": self.createNetwork, 
                          "displayNetwork": self.displayNetwork, 
                          "networks": self.networks}
                execfile(dlg.GetPath(), locals)
            dlg.Destroy()
        
        
        def onOpenConsole(self, event):
            if "_console" not in dir(self):
                import os
                import wx
                from wx import py
                confDir = wx.StandardPaths.Get().GetUserDataDir()
                if not os.path.exists(confDir):
                    os.mkdir(confDir)
                fileName = os.path.join(confDir, 'Console.config')
                self.config = wx.FileConfig(localFilename=fileName)
                self.config.SetRecordDefaults(True)
                locals = {"createNetwork": self.createNetwork, 
                          "displayNetwork": self.displayNetwork, 
                          "networks": self.networks}
                self._console = py.shell.ShellFrame(title="Console", config=self.config, dataDir=confDir, locals=locals)
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
            #network = Network()
            #display.setNetwork(network)
            #regions = {}
            text = 'regions={}\n'
            from realdata import realdata 
            for regionName in realdata.regions:
                props = realdata.regions[regionName]
                label = props[0]
                #region = network.createRegion(label)
                #regions[regionName] = region
                text += 'region = network.createRegion("%s")\nregions["%s"] = region\n' % (regionName, regionName)
                x, y, width, height = props[1][1]
                position = ((x + width / 2 - 50) * 10, ((350 - y) + height / 2) * 10, 0)
                size = (width * 10, height * 10, 100)
                #display.setVisiblePosition(region, position)
                #display.setVisibleSize(region, size)
                text += 'display.setVisiblePosition(region, %s, True)\ndisplay.setVisibleSize(region, %s)\ndisplay.setLabel(region, "%s")\n' % (position, size, label)
            for neuronName in realdata.connections:
                props = realdata.connections[neuronName]
                label = props[0]
                #neuron = network.createNeuron(label)
                text += 'neuron = network.createNeuron("%s")\nneuron.abbreviation = "%s"\n' % (neuronName, label)
                nodeList = props[1]
                #visitedRegions = []
                for node in nodeList:
                    #region = regions[node[1]]
                    #if region not in visitedRegions:
                        #neuron.arborize(region)
                        #visitedRegions.append(region)
                    iob = node[0]
                    if iob == 'o' or iob == 'b':
                        sendsOutput = 'True'
                    else:
                        sendsOutput = 'False'
                    if iob == 'i' or iob == 'b':
                        receivesInput = 'True'
                    else:
                        receivesInput = 'False'
                    text += 'neuron.arborize(regions["%s"], %s, %s)\n' % (node[1], sendsOutput, receivesInput)
            # TODO: region groups
            text += 'display.autoLayout("graphviz")\ndisplay.resetView()\n'
            print text
        
        
        def onOpenInspector(self, event):
            self.inspector.Show(True)
            return self.inspector
        
        
        def onOpenWxinspector(self, event):
            self.ShowInspectionTool()
            
    
    def run():
        # Make sure PyGraphViz can find the command line tools
        # TODO: does this work on Windows?
        import os
        os.environ["PATH"] = os.environ["PATH"] + ":/usr/local/bin:"
    
        app = Neuroptikon(None)
        app.MainLoop()
    
    run( )
    
