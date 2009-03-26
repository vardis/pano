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


import logging
import os, platform
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
from IntroState import IntroState
from resources.DirectoryResourcesLocation import DirectoryResourcesLocation 

class InitGameState(FSMState):
    
    NAME = 'initState'
    
    def __init__(self, gameRef):
        FSMState.__init__(self, gameRef, InitGameState.NAME)
        
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
                              PanoConstants.CVAR_RESOURCES_MODELS : PanoConstants.RES_TYPE_MODELS,
                              PanoConstants.CVAR_RESOURCES_SPRITES : PanoConstants.RES_TYPE_SPRITES,
                              PanoConstants.CVAR_RESOURCES_PLAYLISTS : PanoConstants.RES_TYPE_PLAYLISTS,
                              PanoConstants.CVAR_RESOURCES_SOUNDS : PanoConstants.RES_TYPE_SOUNDS,
                              PanoConstants.CVAR_RESOURCES_VIDEOS : PanoConstants.RES_TYPE_VIDEOS,
                              PanoConstants.CVAR_RESOURCES_MAPPINGS : PanoConstants.RES_TYPE_MAPPINGS,
                              PanoConstants.CVAR_RESOURCES_ITEMS : PanoConstants.RES_TYPE_ITEMS,
                              PanoConstants.CVAR_RESOURCES_SCRIPTS : PanoConstants.RES_TYPE_SCRIPTS
                              }

        res = self.getGame().getResources()
        for config in configs_to_types.keys():
            locations = self.game.getConfig().get(config)
            if locations:
                for path in [str.strip(s) for s in locations.split(',')]:                    
                    loc = DirectoryResourcesLocation(directory=path, name=path, description='', resTypes=configs_to_types[config])
                    res.addResourcesLocation(loc)                
        
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
            
        self.printPlatformInformation() 
        
        game = self.getGame()
        
        # load all configuration variables to game.config
        self.configure()
        
		# configure resource locations
        self.setupResourcesLocations()
                
        # disables Panda's mouse based camera control
        base.disableMouse()
        
        if game.getConfig().getBool(PanoConstants.CVAR_DEBUG_CONSOLE):
            game.enableDebugConsole()
            
        # load global input mappings
        game.getInput().setGlobalMappings('global')                
        
        # sets window settings and hides the system mouse
        winProps = { 
                    PanoConstants.WIN_MOUSE_POINTER : False,
                    PanoConstants.WIN_SIZE : (game.getConfig().getInt(PanoConstants.CVAR_WIN_WIDTH), game.getConfig().getInt(PanoConstants.CVAR_WIN_HEIGHT)),
                    PanoConstants.WIN_FULLSCREEN : game.getConfig().getBool(PanoConstants.CVAR_WIN_FULLSCREEN),
                    PanoConstants.WIN_TITLE : game.getConfig().get(PanoConstants.CVAR_WIN_TITLE)
        }
        game.getView().setWindowProperties(winProps)
        game.getView().openWindow()
        game.getView().initialize()
        
        # init components
        game.getI18n().initialize()        
        game.getMusic().initialize()
#   
    def exit(self):
        pass            
        
    def update(self, millis):
        self.millis += millis
        if self.millis > 2:
            self.getGame().getState().changeState('introState')

    def printPlatformInformation(self):
        di = base.pipe.getDisplayInformation()
        self.log.info('********************')
        self.log.info('Platform Information')
        self.log.info('********************')
        self.log.info('**Platform ID: %s' % platform.platform())
        self.log.info('**CPU ID: %s \t %s' % (di.getCpuVendorString(), di.getCpuBrandString()))
        self.log.info('**Physical memory: %s total, %s available' % (di.getPhysicalMemory(), di.getAvailablePhysicalMemory()))
        self.log.info('**Display driver: ')
        self.log.info('**Shader model: %s' % di.getShaderModel())
        self.log.info('**Texture memory: %s' % di.getTextureMemory())
        self.log.info('**Python version: %s, build: %s' % (platform.python_version(), platform.python_build()))
        
	
