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
from input import InputActionMappings
from resources.ResourceLoader import ResourceLoader
from view.GameView import GameView
from control.InitGameState import InitGameState
from control.ExploreState import ExploreState
from control.PausedState import PausedState
from control.ConsoleState import ConsoleState
from control.IntroState import IntroState
from control.InventoryState import InventoryState
from control.fsm import FSM
from actions.GameActions import GameActions
from resources.i18n import i18n
from audio.music import MusicPlayer
from audio.sounds import SoundsPlayer
from messaging import Messenger
from model.inventory import Inventory


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
        
        self.inventory = Inventory(self)
        
        self.gameView = GameView(gameRef = self, title = name)
        
        self.inputMappings = InputActionMappings(self)
        
        self.i18n = i18n(self)
        
        self.music = MusicPlayer(self)
        
        self.soundsFx = SoundsPlayer(self)
        
        self.msn = Messenger(self)                        
        
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
        pausedState = PausedState(gameRef = self)
        consoleState = ConsoleState(self)
        introState = IntroState(gameRef = self)
        inventoryState = InventoryState(self) 

        self.fsm.addValidState(initState)
        self.fsm.addValidState(exploreState)
        self.fsm.addValidState(pausedState)
        self.fsm.addValidState(consoleState)
        self.fsm.addValidState(introState)
        self.fsm.addValidState(inventoryState)
        self.fsm.changeState(InitGameState.NAME)
        
        # create and start the main game loop task
        self.gameTask = taskMgr.add(self.gameLoop, PanoConstants.TASK_GAME_LOOP)
        
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
                        
        millis = globalClock.getDt() * 1000.0
        
        # process input events
        events = self.inputMappings.getEvents()
        if len(events) > 0:
            for ev, act in events:
                print ev, act
                try:    
                    processed = self.fsm.onInputAction(act)             
                    if not(processed):
                        if self.gameActions.isAction(act):   
                            self.gameActions.execute(act)
                        else:
                            self.log.warning("Ignored unknown input action %s" % act)                    
                                        
                except:
                    self.log.exception("Unexpected error while processing input action %s" % act)        
        
        # update state
        self.fsm.update(millis)       
        
        # update view
        self.gameView.update(millis)
        
        # update sounds
        self.soundsFx.update(millis)     
        
        return Task.cont
            
    def setInitialNode(self, nodeName):
        self.initialNode = nodeName

    def getConfig(self):
        return self.config
        
    def getResources(self):
        return self.resources

    def getState(self):
        return self.fsm
    
    def getInput(self):
        return self.inputMappings

    def getView(self):
        return self.gameView

    def getI18n(self):
        return self.i18n
    
    def getMusic(self):
        return self.music
    
    def getSoundsFx(self):
        return self.soundsFx        
    
    def getInventory(self):
        return self.inventory

    def actions(self):
        return self.gameActions
    
    def canPause(self):
        """
        Use this method to probe whether the game can be paused.
        It returns a boolean that indicates whether the game can be paused at this moment or not.
        @todo: Publish the pause-request event and gather any vetos, for now accept it always. Will probably use the messenger object for this.
        """
        # the current state will decide...
        return self.fsm.allowPausing()
        
    def pause(self):
        """
        Use this method to signal the pausing of the game.        
        @todo: Publish the pause-request event and gather any vetos, for now accept it always.
        """
        if self.canPause():
            self.paused = self.fsm.changeGlobalState(PausedState.NAME)                
    
    def resume(self):
        """
        Use this method to signal the un-pausing of the game.        
        @todo: Publish the pause-request event and gather any vetos, for now accept it always.
        """
        self.fsm.changeGlobalState(self.fsm.getPreviousGlobalState()) 
        self.paused = False    
    
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
#            self.fsm.changeGlobalState(ConsoleState.NAME)
            self.fsm.pushState(ConsoleState.NAME)
            
    def hideDebugConsole(self):
        if self.console is not None:
            self.console.toggle()
            self.consoleVisible = False
#            self.fsm.changeGlobalState(self.fsm.getPreviousGlobalState())
            self.fsm.popState()
            
    def isDebugConsoleVisible(self):
        return self.consoleVisible
    
    def quit(self):
        self.quitRequested = True

#os.chdir(sys.argv[1])

game = PanoGame()
taskMgr.add(game.initialise, "Game initialisation task")
        
run()

