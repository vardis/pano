import sys, os
import logging.config
 
# defer opening of the main window until we read the window properties from the
# configuration and setup a WindowProperties to initialise the window.
from pandac.PandaModules import loadPrcFileData
#loadPrcFileData("", "want-directtools #t")
#loadPrcFileData("", "want-tk #t")
#loadPrcFileData("", "window-type none")
import direct.directbase.DirectStart
 
from pandac.PandaModules import loadPrcFile
from pandac.PandaModules import loadPrcFileData
from pandac.PandaModules import WindowProperties
from direct.task.Task import Task

from external.interactiveConsole.interactiveConsole import pandaConsole, INPUT_CONSOLE, INPUT_GUI, OUTPUT_PYTHON, OUTPUT_IRC

from constants import PanoConstants
from cvars import ConfigVars 
from resources.ResourceLoader import ResourceLoader
from view.GameView import GameView
from control.InitGameState import InitGameState
from control.ExploreState import ExploreState
from control.fsm import FSM
from actions.GameActions import GameActions
from resources.i18n import i18n
from audio.music import MusicPlayer

class PanoGame:
    """
    Runs the game and manages the game tasks and rendering. 
    """
    def __init__(self, name='PanoGame'):
        
        # setup logging
        logging.config.fileConfig('game.cfg')
        self.log = logging.getLogger('pano')
        
        self.name = name                
        self.config = ConfigVars()
        self.windowProperties = {}
        self.parameters = ConfigVars()
        self.resources = ResourceLoader()
        self.gameView = GameView(gameRef = self, title = name)
        self.i18n = i18n(self)
        self.music = MusicPlayer(self)
        self.initialNode = None
        self.mouseMode = PanoConstants.MOUSE_UI_MODE
        self.paused = False

        self.gameActions = GameActions(self) 
        
        self.fsm = None          
        self.gameTask = None

        self.console = None
        self.consoleVisible = False
        
        self.quitRequested = False
        
    def initialise(self, task):
                        
        # setup the game's FSM
        self.fsm = FSM()
        
        initState = InitGameState(gameRef = self)
        exploreState = ExploreState(gameRef = self, node = 'node1')

        self.fsm.addValidState(initState)
        self.fsm.addValidState(exploreState)
        self.fsm.changeState(initState.getName())
        
        # create and start the main game loop task
        self.gameTask = taskMgr.add(self.gameLoop, "Game Loop")
        
        return Task.done
        
    def getConfigVar(self, var, default):
        if self.config.has_key(var):
            return self.config[var]
        else:
            return default
        
    def setConfigVar(self, var, value):
        self.config[var] = value
        
    def gameLoop(self, task):
        """
        Manages the game loop. It is invoked every time a frame is drawn through a Panda Task. 
        """                    
        
        if self.quitRequested:
            return sys.exit()
                
        #update input, graphics, sound, auditing, ai and state
        millis = globalClock.getDt()
        self.fsm.update(millis)       
        
        self.gameView.update(millis)     
        
        return Task.cont
            
    def setInitialNode(self, nodeName):
        self.initialNode = nodeName

    def getConfig(self):
        return self.config
        
    def getResources(self):
        return self.resources

    def getState(self):
        return self.fsm

    def getView(self):
        return self.gameView

    def getI18n(self):
        return self.i18n
    
    def getMusic(self):
        return self.music

    def actions(self):
        return self.gameActions
    
    def isPaused(self):
        return self.paused
    
    def enableDebugConsole(self):
        if self.console is None:
            self.console = pandaConsole( INPUT_GUI|OUTPUT_PYTHON, locals() )
            self.console.toggle()
            
    def showDebugConsole(self):
        if self.console is not None:
            self.console.toggle()
            self.consoleVisible = True
            
    def hideDebugConsole(self):
        if self.console is not None:
            self.console.toggle()
            self.consoleVisible = False
            
    def isDebugConsoleVisible(self):
        return self.consoleVisible
    
    def quit(self):
        self.quitRequested = True

#os.chdir('/host/Documents and Settings/Fidel/workspace/Panorama/demo')

game = PanoGame()
taskMgr.add(game.initialise, "Game initialisation task")
        
run()

