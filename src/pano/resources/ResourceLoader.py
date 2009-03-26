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
import codecs

from constants import PanoConstants
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

class ResourceNotFound(Exception):
    pass

class ResourceLoader:
    """
    Stores all declared resource paths for the various resource types.
    """
    def __init__(self):
        self.log = logging.getLogger('pano.resourceLoader')
               
		# locations of resources indexed by their supported resource types
        self.resLocations = {}		       
        self.parsers = {
                        PanoConstants.RES_TYPE_POINTERS  : PointerParser(),
                        PanoConstants.RES_TYPE_NODES     : NodeParser(),
                        PanoConstants.RES_TYPE_LANGS     : LangFileParser(),
                        PanoConstants.RES_TYPE_FONTS     : FontParser(),
                        PanoConstants.RES_TYPE_SPRITES   : SpriteParser(),
                        PanoConstants.RES_TYPE_PLAYLISTS : PlaylistParser(),
                        PanoConstants.RES_TYPE_MAPPINGS  : ActionMappingsParser(),
                        PanoConstants.RES_TYPE_SOUNDS    : SoundParser(),
                        PanoConstants.RES_TYPE_ITEMS    : InventoryItemParser()
        }
        
    def addResourcesLocation(self, resLoc):
		resTypes = resLoc.getResourcesTypes()
		for type in resTypes:
			if self.resLocations.has_key(type):
				locList = self.resLocations[type]
				locList.append(resLoc)
			else:
				self.resLocations[type] = [ resLoc ]

		# prepare it for lookups
		resLoc.indexResources()
            
    def removeResourcesLocation(self, resLoc):
		resTypes = resLoc.getResourcesTypes()
		for type in resTypes:
			if self.resLocations.has_key(type):
				locList = self.resLocations[type]
				locList.remove(resLoc)
            
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
        node = Node(name=name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_NODES, node, name + '.node')
        except:
            return None
        else:
            return node
        
    def loadFont(self, name):
        font = Font(fontName=name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_FONTS, font, name + '.font')
        except:
            return None
        else:
            return font
    
    def loadPointer(self, name):
        """
        Loads the pointer specified by the given filename. If the pointer was loaded successfully a model.MousePointer
        instance will be returned, otherwise None.
        """
        pointer = MousePointer()
        pointer.setName(name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_POINTERS, pointer, name + '.pointer')
        except:
            return None
        else:
            return pointer                
    
    def loadLangFile(self, name):
        lf = LangFile(name = name)
        language = name[name.index('_') + 1 : name.rindex('.')]
        lf.setLanguage(language)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_LANGS, lf, name + '.lang')
        except:
            return None
        else:
            return lf
        
    def loadSprite(self, name):
        spr = Sprite(name = name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_SPRITES, spr, name + '.spr')
        except:
            return None
        else:
            return spr
    
    def loadPlaylist(self, name):
        mpl = Playlist(name = name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_PLAYLISTS, mpl, name + '.mpl')
        except:
            return None
        else:
            return mpl
        
    def loadActionMappings(self, name):
        mappings = ActionMappings(name, {})
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_MAPPINGS, mappings, name + '.mappings')
        except:
            return None
        else:
            return mappings
        
    def loadSound(self, name):
        sound = Sound(name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_SOUNDS, sound, name + '.sound')
        except:
            return None
        else:
            return sound
        
    def loadItem(self, name):
        item = InventoryItem(name)
        try:
            self.loadGeneric(PanoConstants.RES_TYPE_ITEMS, item, name + '.item')
        except:
            return None
        else:
            return item

    def loadScript(self, name):
        '''
        Loads the content of the specified script file and returns it as a string.
        '''
        filename = name + '.py'
        resPath = self.getResourceFullPath(PanoConstants.RES_TYPE_SCRIPTS, filename)
        istream = None
        try:
            istream = codecs.open(resPath, 'r', "utf-8")
            return istream.read()
        except Exception,e:
            self.log.exception('Failed to load script file: %s' % filename)
        finally:
            if istream is not None: 
                istream.close()

    def loadTexture(self, filename):
        '''
        Loads the texture specified by the given filename.
        Returns: A panda3d Texture object or None if the file was not found.
        '''
        path = self.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, filename)
        return loader.loadTexture(path)
    
    def loadModel(self, filename):
        '''
        Loads the model specified by the given filename.
        Returns: A panda3d ModelNode object or None if the file was not found.
        '''
        path = self.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, filename)
        return loader.loadModel(path)
        
    def loadGeneric(self, resType, resObj, filename):
        assert resType is not None and resType != PanoConstants.RES_TYPE_ALL, 'invalid resource type in loadGeneric'
        resPath = self.getResourceFullPath(resType, filename)
        if resPath is not None:
            istream = None
            try:
                istream = codecs.open(resPath, 'r', "utf-8")
                resource = self.parsers[resType].parse(resObj, istream)
                return resource
            except Exception,e:
                self.log.exception(e)
            finally:
                if istream is not None:
                    istream.close()
        else:
            raise ResourceNotFound('Unable to locate resource %s' % filename)
            
        
