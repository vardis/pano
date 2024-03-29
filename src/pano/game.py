'''
    Copyright (c) 2008 Georgios Giannoudovardis, <vardis.g@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''


from __future__ import with_statement
from __future__ import absolute_import 

import sys, os, codecs
import logging.config
from ConfigParser import SafeConfigParser
 
from pandac.PandaModules import loadPrcFile
from pandac.PandaModules import loadPrcFileData

from pandac.PandaModules import WindowProperties
from direct.task.Task import Task

from external.interactiveConsole.interactiveConsole import pandaConsole, INPUT_CONSOLE, INPUT_GUI, OUTPUT_PYTHON, OUTPUT_IRC

from constants import PanoConstants
from cvars import ConfigVars
from errors.PanoExceptions import *  
from input import InputActionMappings
from resources.ResourceLoader import ResourceLoader
from view.GameView import GameView
from control.InitGameState import InitGameState
from control.ExploreState import ExploreState
from control.PausedState import PausedState
from control.ConsoleState import ConsoleState
from control.IntroState import IntroState
from control.InventoryState import InventoryState
from control.CreditsState import CreditsState
from control.fsm import FSM
from actions.GameActions import GameActions
from resources.i18n import i18n
from audio.music import MusicPlayer
from audio.sounds import SoundsPlayer
from messaging import Messenger
from model.inventory import Inventory
from persistence import *


class PanoGame(object):
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
        self.isGameSequenceActive = False

        self.gameActions = GameActions(self) 
        
        self.fsm = None          
        
        self.gameTask = None

        self.console = None
        self.consoleVisible = False
        
        self.saveLoad = None
        self.saveRequest = None
        self.loadRequest = None
        self.persistence = None
        
        self.quitRequested = False
                    
        # read the boot configuration 
        self._readBootConfig()
        
        os.chdir(self.config.get(PanoConstants.CVAR_GAME_DIR))
        try:
            with open('Config.prc') as cfgFile:
                loadPrcFileData('game-config', cfgFile.read())
        except IOError:
            self.log.exception('Could not find Config.prc in the game directory')
                        
            
    def initialise(self, task):                                                        
                        
        # setup the game's FSM
        self.fsm = FSM('panoFSM', self)
        statesFactory = self.fsm.getFactory()
        statesFactory.registerState(PanoConstants.STATE_INIT, InitGameState)
        statesFactory.registerState(PanoConstants.STATE_EXPLORE, ExploreState)
        statesFactory.registerState(PanoConstants.STATE_PAUSED, PausedState)
        statesFactory.registerState(PanoConstants.STATE_CONSOLE, ConsoleState)
        statesFactory.registerState(PanoConstants.STATE_INTRO, IntroState)
        statesFactory.registerState(PanoConstants.STATE_INVENTORY, InventoryState)
        statesFactory.registerState(PanoConstants.STATE_CREDITS, CreditsState)
        
        self.fsm.changeState(PanoConstants.STATE_INIT)
        
        self.persistence = PersistenceManager()
        self.saveLoad = GameSaveLoad(game = self, savesDir = self.config.get(PanoConstants.CVAR_SAVES_DIR))
        
        # create and start the main game loop task
        globalClock.setMaxDt(0.1)
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
        
        self._doSaveLoad()
        
        # process input events
        events = self.inputMappings.getEvents()
        if len(events) > 0:
            for ev, act in events:
                try:    
                    processed = self.fsm.onInputAction(act)             
                    if not(processed):
                        if self.gameActions.isAction(act):   
                            self.gameActions.execute(act)
                        else:
                            self.log.warning("Ignored unknown input action %s" % act)                    
                                        
                except:
                    self.log.exception("Unexpected error while processing input action %s" % act)        
        
        if self.paused:
            millis = 0
        
        # update state
        self.fsm.update(millis)       
        
        # update view
        self.gameView.update(millis)
        
        # update sounds
        self.soundsFx.update(millis)     
        
        return Task.cont
    
    def initGameSequence(self):
        '''
        Called to prepare the state for a game sequence. For example it could disable user input or hide the mouse pointer.
        '''
        self.gameView.getMousePointer().hide()
        self.inputMappings.disable()
        self.isGameSequenceActive = True
    
    def endGameSequence(self):
        '''
        Called to restore the state after the completion of a game sequence.
        '''
        self.gameView.getMousePointer().show()
        self.inputMappings.enable()
        self.isGameSequenceActive = False

    def getName(self):
        return self.name
            
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

    def getPersistence(self):
        return self.persistence

    def actions(self):
        return self.gameActions
    
    def canPause(self):
        """
        Use this method to probe whether the game can be paused.
        It returns a boolean that indicates whether the game can be paused at this moment or not.
        @todo: Publish the pause-request event and gather any vetos, for now accept it always. Will probably use the messenger object for this.
        """
        # the current state will decide...
        return self.fsm.allowPausing() and not self.isGameSequenceActive
        
    def pause(self):
        """
        Use this method to signal the pausing of the game.        
        @todo: Publish the pause-request event and gather any vetos, for now accept it always.
        """
        if self.canPause():
#            self.paused = self.fsm.changeGlobalState(PausedState.NAME)                
            self.paused = self.fsm.changeGlobalState('pausedState')
            self.paused = True
    
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
            self.console = pandaConsole( self, INPUT_GUI|OUTPUT_PYTHON, locals() )
            self.console.toggle()
            
    def showDebugConsole(self):
        if self.console is not None:
            self.console.toggle()
            self.consoleVisible = True
            self.fsm.pushState('consoleState')
            
    def hideDebugConsole(self):
        if self.console is not None:
            self.console.toggle()
            self.consoleVisible = False
            self.fsm.popState()
            
    def isDebugConsoleVisible(self):
        return self.consoleVisible
    
    def quit(self):
        self.quitRequested = True
        
    def requestSave(self, request):
        self.saveRequest = request
        
    def requestLoad(self, request):
        self.loadRequest = request

    def getInitialNode(self):
        return self.initialNode        

    def _readBootConfig(self):
        '''
        Reads the boot configuration from the user's directory in ~/.pano/<game_name>/.config
        '''        
        self.config.add(PanoConstants.CVAR_GAME_DIR, '.')
        self.config.add(PanoConstants.CVAR_SAVES_DIR, 'saves')
#        userDir = os.path.expanduser('~')
#        bootCfgPath = os.path.join(os.path.join(userDir, self.name), '.config')
#        if os.path.exists(bootCfgPath):
#            cfg = SafeConfigParser()
#            istream = None
#            try:
#                try:
#                    istream = codecs.open(bootCfgPath, 'r', "utf-8")
#                    cfg.readfp(istream)
#                    if cfg.has_option('config', 'game_dir'):
#                        self.gameDir = cfg.get('config', 'game_dir')
#                    else:
#                        self.log.critical('Missing game directory configuration option')
#                        raise GameError('Missing boot config')
#                    if cfg.has_option('config', 'saves_dir'):
#                        self.savesDir = cfg.get('config', 'saves_dir')
#                    else:
#                        self.log.critical('Missing saves directory configuration option')
#                        raise GameError('Missing boot config')
#                except (MissingSectionHeaderError, ParsingError):
#                    self.log.exception('Unexpected error while reading boot config')
#                    raise GameError('Corrupted boot configuration')
#                except IOError, e:
#                    self.log.exception('Unexpected I/O error while reading boot config')
#                    raise GameError('Failed to read boot configuration')
#            finally:
#                if istream is not None:
#                    istream.close()
#        else:
#            self.log.critical('Missing boot configuration, cannot properly initialize')
#            raise GameError('Failed boot init')

    def _doSaveLoad(self):
        '''
        Checks for a pending save or load request and performs the respective operation.
        If the operation succeeds the PanoConstants.EVENT_LOAD_COMPLETED or PanoConstants.EVENT_SAVE_COMPLETED
        event will be send.
        If the operation failed the PanoConstants.EVENT_SAVELOAD_ERROR event will be send.
        '''
        if self.saveRequest is not None:            
            try:
                self.saveLoad.save(self.persistence, self.saveRequest)
            except SaveGameError:
                self.log.exception('Save action failed due to unexpected error.')
                self.msn.sendMessage(PanoConstants.EVENT_SAVELOAD_ERROR, [self.saveRequest])
            else:
                self.msn.sendMessage(PanoConstants.EVENT_SAVE_COMPLETED, [self.saveRequest])                    
            finally:
                self.saveRequest = None
                    
        elif self.loadRequest is not None:            
            try:
                self.saveLoad.load(self.persistence, self.loadRequest)
            except LoadGameError:
                self.log.exception('Load action failed due to unexpected error.')
                self.msn.sendMessage(PanoConstants.EVENT_SAVELOAD_ERROR, [self.loadRequest])
            else:
                self.msn.sendMessage(PanoConstants.EVENT_LOAD_COMPLETED, [self.loadRequest])                
            finally:
                self.loadRequest = None


game = PanoGame()

import direct.directbase.DirectStart

taskMgr.add(game.initialise, "Game initialisation task")
        
run()

