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
import os.path
import logging
import codecs
import weakref

from pandac.PandaModules import NodePath

from constants import PanoConstants
from ResourcesTypes import ResourcesTypes
from DirectoryResourcesLocation import DirectoryResourcesLocation
from model.Node import Node
from model.LangFile import LangFile
from model.MousePointer import MousePointer
from model.Font import Font
from model.Sprite import Sprite
from model.Playlist import Playlist
from model.ActionMappings import ActionMappings
from model.Sound import Sound
from model.InventoryItem import InventoryItem
from parsers.PointerParser import PointerParser 
from parsers.NodeParser import NodeParser
from parsers.FontParser import FontParser
from parsers.LangFileParser import LangFileParser
from parsers.SpriteParser import SpriteParser
from parsers.PlaylistParser import PlaylistParser
from parsers.ActionMappingsParser import ActionMappingsParser
from parsers.SoundParser import SoundParser
from parsers.InventoryItemParser import InventoryItemParser
from errors.PanoExceptions import ResourceNotFound


class ResourceLoader:
    """
    Stores all declared resource paths for the various resource types.
    """
    def __init__(self):
        self.log = logging.getLogger('pano.resourceLoader')
               
        # locations of resources indexed by their supported resource types
        self.resLocations = {}
        self.locationsByName = {}               
        self.parsers = {
                        PanoConstants.RES_TYPE_POINTERS     : PointerParser(),
                        PanoConstants.RES_TYPE_NODES        : NodeParser(),
                        PanoConstants.RES_TYPE_LANGS        : LangFileParser(),
                        PanoConstants.RES_TYPE_FONTS        : FontParser(),
                        PanoConstants.RES_TYPE_SPRITES      : SpriteParser(),
                        PanoConstants.RES_TYPE_PLAYLISTS    : PlaylistParser(),
                        PanoConstants.RES_TYPE_MAPPINGS     : ActionMappingsParser(),
                        PanoConstants.RES_TYPE_SOUNDS_DEFS  : SoundParser(),
                        PanoConstants.RES_TYPE_ITEMS        : InventoryItemParser()
        }
        
        # caches loaded resources but uses weak references to avoid storing large objects when they are no longer used
        self.cache = weakref.WeakValueDictionary()
        
        # stores resources that should be loaded because of a call to preloadResources or preloadResourceLocation        
        self.preloadStore = {}

        
    def addResourcesLocation(self, resLoc):
        resTypes = resLoc.getResourcesTypes()
        for type in resTypes:
            if self.resLocations.has_key(type):
                locList = self.resLocations[type]
                locList.append(resLoc)
            else:
                self.resLocations[type] = [ resLoc ]

        self.locationsByName[resLoc.getName()] = resLoc
        
        # prepare it for lookups
        resLoc.indexResources()
            
    def removeResourcesLocation(self, resLoc):
        resTypes = resLoc.getResourcesTypes()
        for type in resTypes:
            if self.resLocations.has_key(type):
                locList = self.resLocations[type]
                locList.remove(resLoc)
                
        if resLoc.getName() in self.locationsByName:
            del self.locationsByName[resLoc.getName()]
            
    def getResourceFullPath(self, resType, filename):                
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            if locations is not None:
                for loc in locations:
                    if loc.containsResource(filename):
                        return loc.getResourceFullPath(filename)
        return None

    def openResourceStream(self, resType, filename):
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            if locations is not None:
                for loc in locations:
                    if loc.containsResource(filename):
                        return loc.getResourceStream(filename)
        return None
    
    def listResources(self, resType, fullPaths=True):
        res = []
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            if locations is not None:
                for loc in locations:
                    res.extend(loc.listResources(resType, fullPaths))
        return res           
    
    def loadAllLangFiles(self):
        filenames = self.listResources(PanoConstants.RES_TYPE_LANGS, False)
        if filenames:
            return [lf for lf in [self.loadLangFile(f[:-5]) for f in filenames] if lf is not None]
        else:
            return []
        
    def loadAllFonts(self):
        filenames = self.listResources(PanoConstants.RES_TYPE_FONTS, False)
        if filenames:
            return [ff for ff in [self.loadFont(f[:-5]) for f in filenames] if ff is not None]
        else:
            return []
    
    def loadNode(self, name):        
        return self.loadGeneric(PanoConstants.RES_TYPE_NODES, name, name + '.node')
                
    def loadFont(self, name):        
        return self.loadGeneric(PanoConstants.RES_TYPE_FONTS, name, name + '.font')        
    
    def loadPointer(self, name):
        """
        Loads the pointer specified by the given filename. If the pointer was loaded successfully a model.MousePointer
        instance will be returned, otherwise None.
        """
        return self.loadGeneric(PanoConstants.RES_TYPE_POINTERS, name, name + '.pointer')        
    
    def loadLangFile(self, name):        
        langFile = self.loadGeneric(PanoConstants.RES_TYPE_LANGS, name, name + '.lang')        
        return langFile
        
    def loadSprite(self, name):
        return self.loadGeneric(PanoConstants.RES_TYPE_SPRITES, name, name + '.spr')        
    
    def loadPlaylist(self, name):
        return self.loadGeneric(PanoConstants.RES_TYPE_PLAYLISTS, name, name + '.mpl')
                
    def loadActionMappings(self, name):
        return self.loadGeneric(PanoConstants.RES_TYPE_MAPPINGS, name, name + '.mappings')        
        
    def loadSound(self, name):
        return self.loadGeneric(PanoConstants.RES_TYPE_SOUNDS_DEFS, name, name + '.sound')
                
    def loadItem(self, name):        
        return self.loadGeneric(PanoConstants.RES_TYPE_ITEMS, name, name + '.item')        

    def loadScript(self, name):
        '''
        Loads the content of the specified script file and returns it as a string.
        '''
        filename = name + '.py'
#        resPath = self.getResourceFullPath(PanoConstants.RES_TYPE_SCRIPTS, filename)        
        return self.loadText(filename)

    def loadTexture(self, filename):
        '''
        Loads the texture specified by the given filename.
        Returns: A panda3d Texture object or None if the file was not found.
        '''
        path = self.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, filename)
        tex = self._fetchPreloaded(path)        
        return tex if tex is not None else loader.loadTexture(path)
    
    def loadModel(self, filename):
        '''
        Loads the model specified by the given filename.
        Returns: A panda3d ModelNode object or None if the file was not found.
        '''
        path = self.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, filename)
#        return loader.loadModel(path)
        model = self._fetchPreloaded(path)
        return model if model is not None else loader.loadModel(path)    
        
    
        
    def loadGeneric(self, resType, resName, filename, fullPath = False):
        assert resType is not None and resType != PanoConstants.RES_TYPE_ALL, 'invalid resource type in loadGeneric'
        
        if fullPath:
            resPath = filename
        else:
            resPath = self.getResourceFullPath(resType, filename)
            
        if resPath is not None:
        
            resObj = self._fetchPreloaded(resPath)
            if resObj is not None:
                return resObj            
            
            istream = None
            try:
                istream = codecs.open(resPath, 'r', "utf-8")
                resObj = ResourcesTypes.constructParsedResource(resType, resName)
                resource = self.parsers[resType].parse(resObj, istream)
                return resource
            except Exception,e:
                self.log.exception(e)
            finally:
                if istream is not None:
                    istream.close()
        else:
            raise ResourceNotFound(filename)
        
    def loadText(self, filename, encoding = "utf-8"):
        
        if self.preloadStore.has_key(filename):
            return self.preloadStore[filename]
                
        try:
            resPath = self.getResourceFullPath(PanoConstants.RES_TYPE_TEXTS, filename)
            with codecs.open(resPath, 'r', encoding) as istream:
                return istream.read()
        except Exception,e:
            raise ResourceNotFound(filename)
    
    def loadBinary(self, filename):        
        
        if self.preloadStore.has_key(filename):
            return self.preloadStore[filename]
        
        try:
            resPath = self.getResourceFullPath(PanoConstants.RES_TYPE_BINARIES, filename)
            with open(resPath, 'r') as istream:
                return istream.read()
        except Exception,e:
            raise ResourceNotFound(filename)
        
    def listResourceLocations(self):
        for loc in self.locationsByName.values():            
            self.log.debug(loc)            
            
    def preloadResources(self, resType):
        '''
        Pre-loads all discovered resources of the given type.
        For example preloadResources(PanoConstants.RES_TYPE_MODELS) will pre-load all models in all resource locations
        '''
        locations = self.resLocations.get(resType)
        if locations is not None:
            for loc in locations:
                self.preloadResourceLocation(loc.getName(), [resType], False)                        
    
    def preloadResourceLocation(self, locName, resourceTypes = None, clearPreloadStore = False):
        '''
        Pre-loads all resources contained in the specified resource locations. You can also used the resType parameter
        to control what type of resources you want to be loaded.
        '''
        
        if clearPreloadStore:
            self.preloadStore.clear()
        
        loc = self.locationsByName.get(locName)
        if loc is not None:
            
            # if the types to preload is omitted then set to load only the supported types of the resource location 
            typesToPreload = resourceTypes
            if typesToPreload is None:
                typesToPreload = loc.getResourcesTypes()
            
            for resType in typesToPreload:
                resPaths = loc.listResources(resType, True)                
                for filename in resPaths:
                    resObj = self._loadInternal(resType, filename, loc)
                    self._storePreloaded(resObj, resType, filename)
                    
                    
    def _storePreloaded(self, res, resType, filename):
        '''
        Stores a pre-loaded resources.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('adding pre-loaded resource %s of type %s, resource class type %s' % (filename, resType, type(res)))
            
#        if not self.preloadStore.has_key(resType):
#            self.preloadStore[resType] = {}
#            
#        fmap = self.preloadStore[resType]
#        fmap[filename] = res
        self.preloadStore[filename] = res                
            
    def _fetchPreloaded(self, filename, resType = None):
#        fmap = self.preloadStore.get(resType)
#        if fmap is not None:
#            res = fmap.get(filename)
#            if type(res) == NodePath and res.isEmpty():
#                self._reloadResource()

        res = self.preloadStore.get(filename)
        if res is not None:
            if type(res) == NodePath and res.isEmpty():
                if self.log.isEnabledFor(logging.DEBUG):
                    self.log.debug('scenegraph resource was stale, re-loading from file %s' % filename)
                return None
            else:
                return res
        else:                 
            return None
                
    def _loadInternal(self, resType, filename, location):
        '''
        '''
        if ResourcesTypes.isParsedResource(resType):                        
            # construct resource name from the basename of the filename and dropping the extension
            resName = os.path.basename(filename)
            resName = resName[:resName.find('.')]
                                    
            return self.loadGeneric(resType, resName, filename, True)            
            
        elif ResourcesTypes.isPandaResource(resType):
            if resType == PanoConstants.RES_TYPE_MODELS:
                return loader.loadModel(filename)
                
            elif resType == PanoConstants.RES_TYPE_TEXTURES or resType == PanoConstants.RES_TYPE_VIDEOS:    
                return loader.loadTexture(filename)
                
            elif resType == PanoConstants.RES_TYPE_MUSIC:
                return loader.loadMusic(filename)
                
            elif resType == PanoConstants.RES_TYPE_SFX:
                return loader.loadSfx(filename)
                
        elif ResourcesTypes.isStreamResource(resType):
            if resType == PanoConstants.RES_TYPE_SCRIPTS:
                return self.loadText(filename)
            else:
                return self.loadBinary(filename)
                
            
        
