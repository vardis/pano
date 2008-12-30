import sys
import logging.config
 
# defer opening of the main window until we read the window properties from the
# configuration and setup a WindowProperties to initialise the window.
#loadPrcFileData("", "window-type none")
import direct.directbase.DirectStart
 
from pandac.PandaModules import loadPrcFile
from pandac.PandaModules import loadPrcFileData
from pandac.PandaModules import WindowProperties
from direct.task.Task import Task

from constants import PanoConstants
from parameters import PanoParameters 
from resources.ResourceLoader import ResourceLoader
from view.GameView import GameView
from control.InitGameState import InitGameState
from control.ExploreState import ExploreState
from control.fsm import FSM
from actions.GameActions import GameActions

class PanoGame:
    """
    Runs the game and manages the game tasks and rendering. 
    """
    def __init__(self, name='PanoGame'):
        
        # setup logging
        logging.config.fileConfig('game.cfg')
        self.log = logging.getLogger('pano')
        
        self.name = name                
        self.config = None
        self.parameters = PanoParameters()
        self.resources = ResourceLoader()
        self.gameView = GameView(gameRef = self, title = name)
        self.initialNode = None
        self.mouseMode = PanoConstants.MOUSE_UI_MODE
        self.paused = False

        self.gameActions = GameActions(self) 
        
        self.fsm = None          
        self.gameTask = None
        
        self.quitRequested = False
        
    def initialise(self, task):
                                
        self.config = loadPrcFile(PanoConstants.CONFIG_FILE)
        
        # override setting for the mouse cursor and let the other window properties
        # get their values from the configuration file or the default Panda values
        winProps = { PanoConstants.WIN_MOUSE_POINTER : False }
        self.gameView.setWindowProperties(winProps)
        
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
        
    def getResources(self):
        return self.resources

    def getState(self):
        return self.fsm

    def getView(self):
        return self.gameView

    def actions(self):
        return self.gameActions
    
    def isPaused(self):
        return self.paused
    
    def quit(self):
        self.quitRequested = True

game = PanoGame()
taskMgr.add(game.initialise, "Game initialisation task")
        
run()

print 'exit'            
            