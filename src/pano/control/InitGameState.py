import logging
import os
from ConfigParser import SafeConfigParser

from pandac.PandaModules import getModelPath
from pandac.PandaModules import getTexturePath
from pandac.PandaModules import getSoundPath
from pandac.PandaModules import ConfigVariableString
from pandac.PandaModules import Filename
from pandac.PandaModules import Notify
from pandac.PandaModules import MultiplexStream

from constants import PanoConstants 
from fsm import FSMState
from model.Node import Node
from model.Hotspot import Hotspot
from ExploreState import ExploreState
from resources.DirectoryResourcesLocation import DirectoryResourcesLocation 

class InitGameState(FSMState):
    def __init__(self, gameRef):
        FSMState.__init__(self, gameRef, 'InitGameState')
        
        self.log = logging.getLogger('pano.initState')        
        self.millis = 0
        
    def setupResourcesLocations(self):

        # as the resource paths are relative to the currently working directory, we add '.' to the model path	
        getModelPath( ).appendPath( os.getcwd( ) )
        getTexturePath( ).appendPath( os.getcwd( ) )
        getSoundPath( ).appendPath( os.getcwd( ) )        

        # add resource locations
        configs_to_types = {
                              PanoConstants.CVAR_RESOURCES_NODES : PanoConstants.RES_TYPE_NODES,
                              PanoConstants.CVAR_RESOURCES_TEXTURES : PanoConstants.RES_TYPE_TEXTURES,
                              PanoConstants.CVAR_RESOURCES_FONTS : PanoConstants.RES_TYPE_FONTS,
                              PanoConstants.CVAR_RESOURCES_POINTERS : PanoConstants.RES_TYPE_POINTERS,
                              PanoConstants.CVAR_RESOURCES_LANGS : PanoConstants.RES_TYPE_LANGS,
                              PanoConstants.CVAR_RESOURCES_MODELS : PanoConstants.RES_TYPE_MODELS
                              }

        res = self.getGame().getResources()
        for config in configs_to_types.keys():
            locations = self.game.getConfig().get(config)
            if locations:
                for path in [str.strip(s) for s in locations.split(',')]:                    
                    loc = DirectoryResourcesLocation(directory=path, name=path, description='', resTypes=configs_to_types[config])
                    res.addResourcesLocation(loc)
                    
        print res.listResources(PanoConstants.RES_TYPE_TEXTURES)
        
    def configure(self):
        
        vars = self.game.getConfig()        
        istream = None        
        try:
            istream = open('game.cfg', 'r')
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            sections = cfg.sections()
            for s in sections:
                if not (s.startswith('logger') or s.startswith('handler') or s.startswith('formatter')):                 
                    options = cfg.options(s)
                    for opt in options:                        
                        vars.add(s + '_' + opt, cfg.get(s, opt))
                
        finally:
            if istream is not None:
                istream.close()
                
        
    def enter(self):
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('entered initial state') 
        
        self.configure()
        
		# configure resource locations
        self.setupResourcesLocations()
                
        # disables Panda's mouse based camera control
        base.disableMouse()
        
        self.getGame().getI18n().initialize()
        
        # sets window settings and hides the system mouse
        winProps = { 
                    PanoConstants.WIN_MOUSE_POINTER : False,
                    PanoConstants.WIN_SIZE : (self.game.getConfig().getInt(PanoConstants.CVAR_WIN_WIDTH), self.game.getConfig().getInt(PanoConstants.CVAR_WIN_HEIGHT)),
                    PanoConstants.WIN_FULLSCREEN : self.game.getConfig().getBool(PanoConstants.CVAR_WIN_FULLSCREEN),
                    PanoConstants.WIN_TITLE : self.game.getConfig().get(PanoConstants.CVAR_WIN_TITLE)
        }
        self.getGame().getView().setWindowProperties(winProps)
        self.getGame().getView().openWindow()
        self.getGame().getView().initialize()        
                    
        self.initialNode = self.getGame().getResources().loadNode('node1')        
                
        
        self.getGame().getView().displayNode(self.initialNode)                
        self.getGame().getView().mousePointer.setByName('select')
        talkBox = self.getGame().getView().getTalkBox()
#        talkBox.showText(
#"""
#Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et 
#dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip 
#ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
#eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia 
#deserunt mollit anim id est laborum.
#""", (1,0,0,1))
#        talkBox.showText("A small line of code through: \nself.getGame().getView().getTalkBox().showText(...)")
        
    def exit(self):
        pass            
        
    def update(self, millis):
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('initial state update %d', millis)                    
        self.millis += millis
        if self.millis > 2:
            self.getGame().getState().changeState(ExploreState.NAME)

	
