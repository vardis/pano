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



import os, cPickle
import datetime, logging

from constants import PanoConstants
from pano.exceptions.PanoExceptions import *
from messaging import Messenger

class PersistenceContext:
    def __init__(self, name):
        self.name = name
        self.vars = {}
    
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def addVar(self, varName, value):
        self.vars[varName] = value

    def removeVar(self, varName):
        del self.vars[varName]
        
    def getVar(self, varName):
        return self.vars[varName] if self.hasVar(varName) else None        

    def hasVar(self, varName):
        return self.vars.has_key(varName)

        
class PersistenceManager:
    def __init__(self):
        pass
    
    def createContext(self, name):
        return PersistenceContext(name)
    
    def serializeContext(self, ctx):
        return cPickle.dumps(ctx, cPickle.HIGHEST_PROTOCOL)
    
    def deserializeContext(self, stream):
        return cPickle.loads(stream)
    
    def writeContext(self, ctx, filename):
        fp = None
        try:
            fp = open(filename, 'w')
            fp.write(self.serializeContext(ctx))
        except IOError,e:
            self.log.exception('Failed to write context: %s to file' % (ctx.getName(), filename))
        finally:
            if fp is not None:
                fp.close()

    def readContext(self, filename):
        fp = None
        try:
            fp = open(filename, 'r')
            return self.deserializeContext(fp.read())
        except IOError,e:
            self.log.exception('Failed to read context: %s from file' % (ctx.getName(), filename))
        finally:
            if fp is not None:
                fp.close()
    

class SavedGameData:
    '''
    Stores saved game data.
    '''
    def __init__(self):
        self.name = ''
        self.version = 1.0
        self.screenshot = None
        self.datetime = None
        self.activeNode = None
        self.gameCtx = None
        self.fsmCtx = None
        self.inventoryCtx = None

    def getName(self):
        return self.name
    
    def getVersion(self):
        return self.version
    
    def getScreenshot(self):
        return self.screenshot
    
    def getDatetime(self):
        return self.datetime
    
    def getActiveNode(self):
        return self.activeNode

    def getGameCtx(self):
        return self.gameCtx


    def getFsmCtx(self):
        return self.fsmCtx


    def getInventoryCtx(self):
        return self.inventoryCtx

    def setName(self, name):
        self.name = name
    
    def setVersion(self, version):
        self.version = version
    
    def setScreenshot(self, screenshot):
        self.screenshot = screenshot
    
    def setDatetime(self, datetime):
        self.datetime = datetime

    def setActiveNode(self, activeNode):
        self.activeNode = activeNode

    def setGameCtx(self, value):
        self.gameCtx = value


    def setFsmCtx(self, value):
        self.fsmCtx = value


    def setInventoryCtx(self, value):
        self.inventoryCtx = value


class GameSaveLoad:
    
    DATE_FORMAT = '%a_%b_%d_%H%M%S_%Y'
    
    def __init__(self, game, savesDir = 'saves'):
        self.log = logging.getLogger('pano.saveLoad')
        self.game = game
        self.savesDir = savesDir
        self.pm = PersistenceManager()
    
    def getSavesDir(self):
        '''
        Returns the path to the directory that contains the saved games. The returned path is local to the game's directory.
        '''
        return self.savesDir
    
    def setSavesDir(self, dir):
        '''
        Sets the directory where new saved games should be stored.
        '''
        self.savesDir = dir
    
    def getSavesList(self):
        '''
        Returns a list of SavedGameData instances that represent the saved games located in the current
        saves directory. To get the currently active saves directory use GameSaveLoad.getSavesDir()
        '''
        return [] 
    
    def save(self, name):
        
        save = SavedGameData()        
        
        # save the state of the various game components into persistence contexts
        gameCtx = self.game.persistState(self.pm)       
        fsmCtx = self.game.getState().persistState(self.pm)                     
        inventoryCtx = self.game.getInventory().persistState(self.pm)
        # in the future, add more here...
        
        dt = datetime.datetime.now()
        savePrefix = name #+ '_' + dt.strftime(self.DATE_FORMAT)
        saveName = savePrefix + '.sav'
        screenName = savePrefix + '.jpg'
        
        try:
            self.game.getView().saveScreenshot(os.path.join(self.savesDir, screenName))
        except GraphicsError, e:
            self.log.exception('Unexpected error while saving screenshot.')
            raise SaveGameError('Could not save game')
        
        save.setVersion(1.0)
        save.setName(self.game.getName())
        save.setDatetime(dt) 
        save.setScreenshot(screenName)
        save.setActiveNode(self.game.getView().getActiveNode().getName())
        
        # serialize (pickle) all gathered contexts
        try:
            save.setGameCtx(self.pm.serializeContext(gameCtx))
            save.setInventoryCtx(self.pm.serializeContext(inventoryCtx))
            save.setFsmCtx(self.pm.serializeContext(fsmCtx))
            # in the future, add more here...
        except PersistenceError, e:
            self.log.exception('Unexpected error while serializing data.')            
            
        # write the data
        fp = None
        try:
            fp = open(os.path.join(self.savesDir, saveName), 'w')            
            fp.write(cPickle.dumps(save))
        except IOError, e:
            self.log.exception('Unexpected error while writing saved game.')
            raise SaveGameError('Failed to write saved game file.')
        finally:
            if fp is not None:
                fp.close()
        
    
    def load(self, saveName):       
        fp = None 
        try:
            fp = open(os.path.join(self.savesDir, saveName + '.sav'), 'r')
            save = cPickle.load(fp)
            if save.getVersion() != 1.0:
                raise LoadGameError('Save file corresponds to an incompatible version of this game.')
            
            print save.getName()
                        
            print 'Saved game was created at %s' % save.getDatetime().strftime(self.DATE_FORMAT)
            
            # de-serialize pickled contexts
            try:
                gameCtx = self.pm.deserializeContext(save.getGameCtx())
                inventoryCtx = self.pm.deserializeContext(save.getInventoryCtx())    
                fsmCtx = self.pm.deserializeContext(save.getFsmCtx())        
            except PersistenceError, e:
                self.log.exception('Unexpected error while deserializing data.')
                raise LoadGameError('Failed to read serialized data.')
            
            # load back the states
            self.game.restoreState(self.pm, gameCtx)
            self.game.getInventory().restoreState(self.pm, inventoryCtx)
            self.game.getState().restoreState(fsmCtx)
            # more to follow...
            
#            msn = Messenger(self)
#            msn.sendMessage(PanoConstants.EVENT_RESTORE_NODE, [save.getActiveNode(), nodescriptCtx])
            
        except IOError, e:
            self.log.exception('Unexpected error while reading saved game.')
            raise LoadGameError('Failed to read saved game data.')
        
        finally:
            if fp is not None:
                fp.close()                
                
                
        
        
    
    