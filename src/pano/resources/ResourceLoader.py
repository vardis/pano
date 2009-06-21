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

from pandac.PandaModules import NodePath
from pandac.PandaModules import Shader

from pano.constants import PanoConstants
from pano.util.Cache import Cache
from pano.resources.Resource import Resource
from pano.resources.ResourcesTypes import ResourcesTypes
from pano.resources.parsers.PointerParser import PointerParser
from pano.resources.parsers.NodeParser import NodeParser
from pano.resources.parsers.FontParser import FontParser
from pano.resources.parsers.LangFileParser import LangFileParser
from pano.resources.parsers.SpriteParser import SpriteParser
from pano.resources.parsers.PlaylistParser import PlaylistParser
from pano.resources.parsers.ActionMappingsParser import ActionMappingsParser
from pano.resources.parsers.SoundParser import SoundParser
from pano.resources.parsers.InventoryItemParser import InventoryItemParser
from pano.errors.PanoExceptions import ResourceNotFound


class ResourceLoader(object):
    """
    Stores all declared resource paths for the various resource types.
    """
    def __init__(self):
        self.log = logging.getLogger('pano.resourceLoader')

        # Locations of resources indexed by their supported resource types.
        self.resLocations = {}
        
        # Locations of resources indexed by their names
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

        # Caches loaded resources but uses weak references to avoid storing large objects when
        # they are no longer used.
        self.cache = Cache('resources')

        # Stores resources that should be loaded because of a call to preloadResources or
        # preloadResourceLocation.
        # It is organized as: { res_location_name : { res_filename : resource } }
        self.preloadStore = {}

        # Stores resources that should remain loaded for all lifetime of the game.
        # It is organized as: { res_filename : (BaseResource instance, resourceType, resource location name)
        self.stickyResources = {}

        # statistics
        self.requests = 0
        self.preloadHits = 0
        self.preloadMisses = 0
        self.stickyLoads = 0


    def addResourcesLocation(self, resLoc):
        '''
        Adds a resources location to the list of location that will be indexed and searched for supported
        resource types.
        @param resLoc: An object that extends pano.resources.AbstractResourceLocation.
        '''
        resTypes = resLoc.getResourcesTypes()
        for type in resTypes:
            if self.resLocations.has_key(type):
                locList = self.resLocations[type]
                locList.append(resLoc)
            else:
                self.resLocations[type] = [ resLoc ]

        self.locationsByName[resLoc.name] = resLoc

        # prepare it for lookups
        resLoc.indexResources()


    def removeResourcesLocation(self, resLoc):
        '''
        Removes a resource location from the list of known locations. 
        @param resLoc: An object that extends pano.resources.AbstractResourceLocation.
        '''
        resTypes = resLoc.getResourcesTypes()
        for type in resTypes:
            if self.resLocations.has_key(type):
                locList = self.resLocations[type]
                locList.remove(resLoc)

        if self.locationsByName.has_key(resLoc.name):
            del self.locationsByName[resLoc.name]


    def getResourceFullPath(self, resType, filename):
        '''
        Gets the absolute filesystem path to the resource.
        @param resType: A constant that identifies the type of the resource.
        @param filename: The basename of the resource file.
        @return: The full path to the resource file.
        '''
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            if locations is not None:
                for loc in locations:
                    if loc.containsResource(filename):
                        return loc.getResourceFullPath(filename)
        return None


    def locateResource(self, resType, filename):
        '''
        Locates a resource by return the ResourceLocation that contains it.
        @param resType: A constant that identifies the type of the resource.
        @param filename: The basename of the resource file.
        '''
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            for loc in locations:
                if loc.containsResource(filename):
                    return loc
        return None


    def openResourceStream(self, resType, filename):
        '''
        Opens a data stream to the specified resource.
        @param resType: A constant that identifies the type of the resource.
        @param filename: The basename of the resource file.
        @return: A stream used for reading te contents of the resource.
        '''
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            if locations is not None:
                for loc in locations:
                    if loc.containsResource(filename):
                        return loc.getResourceStream(filename)
        return None


    def listResources(self, resType, fullPaths=True):
        '''
        Lists all resources of the given type that are contained in all specified resource locations.
        @param resType: A constant that identifies the type of the resource.
        @param fullPaths: If True the resource filenames will get returned as full paths.
        '''
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
        '''
        Loads the shader specified by the given name.
        @param name: The name of the node, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.Node instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.node' if not name.endswith('.node') else name
        return self._loadInternal(PanoConstants.RES_TYPE_NODES, filename)


    def loadFont(self, name):
        '''
        Loads the font definition specified by the given name.
        @param name: The name of the font definition, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.Font instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.font' if not name.endswith('.font') else name
        return self._loadInternal(PanoConstants.RES_TYPE_FONTS, filename)


    def loadPointer(self, name):        
        '''
        Loads the mouse pointer specified by the given name.
        @param name: The name of the pointer, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.MousePointer instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.pointer' if not name.endswith('.pointer') else name
        return self._loadInternal(PanoConstants.RES_TYPE_POINTERS, filename)


    def loadLangFile(self, name):
        '''
        Loads the language file specified by the given name.
        @param name: The name of the language file, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.LangFile instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.lang' if not name.endswith('.lang') else name
        return self._loadInternal(PanoConstants.RES_TYPE_LANGS, filename)


    def loadSprite(self, name):
        '''
        Loads the sprite definition specified by the given name.
        @param name: The name of the sprite, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.Sprite instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.spr' if not name.endswith('.spr') else name
        return self._loadInternal(PanoConstants.RES_TYPE_SPRITES, filename)


    def loadPlaylist(self, name):
        '''
        Loads the music playilst specified by the given name.
        @param name: The name of the playilst, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.Playlist instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.mpl' if not name.endswith('.mpl') else name
        return self._loadInternal(PanoConstants.RES_TYPE_PLAYLISTS, filename)


    def loadActionMappings(self, name):
        '''
        Loads the action mappings specified by the given name.
        @param name: The name of the mappings, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.ActionMappings instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.mappings' if not name.endswith('.mappings') else name
        return self._loadInternal(PanoConstants.RES_TYPE_MAPPINGS, filename)


    def loadSound(self, name):
        '''
        Loads the sound definition specified by the given name.
        @param name: The name of the sound, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.Sound instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.sound' if not name.endswith('.sound') else name
        return self._loadInternal(PanoConstants.RES_TYPE_SOUNDS_DEFS, filename)


    def loadItem(self, name):
        '''
        Loads the inventory item definition specified by the given name.
        @param name: The name of the item, by convention it will be used as the basename
        of the file to load.
        @return: A pano.model.InventoryItem instance or None if the file was not found or could not get loaded.
        '''
        filename = name + '.item' if not name.endswith('.item') else name
        return self._loadInternal(PanoConstants.RES_TYPE_ITEMS, filename)


    def loadScript(self, name):
        '''
        Loads the script specified by the given name.
        @param name: The name of the script, by convention it will be used as the basename
        of the file to load.
        @return: The script file contents as a string.
        '''
        filename = name + '.py' if not name.endswith('.py') else name
        return self._loadInternal(PanoConstants.RES_TYPE_SCRIPTS, filename)


    def loadTexture(self, filename):
        '''
        Loads the texture specified by the given filename.
        @param filename: The filename of the texture.
        @return: A pandac.PandaModules.Texture object or None if the file was not found.
        '''
        return self._loadInternal(PanoConstants.RES_TYPE_TEXTURES, filename)


    def loadModel(self, filename):
        '''
        Loads the model specified by the given filename.
        @param filename: The filename of the model.
        @return: A pandac.PandaModules.NodePath object or None if the file was not found.
        '''
        return self._loadInternal(PanoConstants.RES_TYPE_MODELS, filename)


    def loadShader(self, name):
        '''
        Loads the shader specified by the given name.
        @param name: The name of the shader, by convention it will be used as the basename
        of the shader file to load.
        @return: A pandac.PandaModules.Shader instance or None if the file was not found or could not get loaded.
        '''
        exts = ResourcesTypes.getExtensions(PanoConstants.RES_TYPE_SHADERS)
        if len(exts) == 1:
            return self._loadInternal(PanoConstants.RES_TYPE_SHADERS, name + exts[0])
        else:
            return self._loadInternal(PanoConstants.RES_TYPE_SHADERS, name)


    def loadText(self, filename, encoding = "utf-8"):
        '''
        Loads the text based resource with the given filename, the decoding of the characters is based on the
        specified encoding which defaults to utf-8.
        @param filename: The full path to the file that contains the resource.
        @param encoding: The encoding to use for interpreting the characters.
        @return: A string object that has the file contents or None if loading failed.
        '''
        return self._loadCharacterStream(filename, encoding)


    def loadBinary(self, filename):
        '''
        Loads the given filename as a stream of bytes.
        @param filename: The full path to the file that contains the resource.
        @return: A string object that has the file contents or None if loading failed.
        '''
        return self._loadBinaryStream(filename)


    def listResourceLocations(self):
        for loc in self.locationsByName.values():
            self.log.debug(loc)


    def preloadResources(self, resType):
        '''
        Pre-loads all discovered resources of the given type.
        For example preloadResources(PanoConstants.RES_TYPE_MODELS) will pre-load all models in all resource
        locations.
        @param resType: A constant that identifies the type of resources to preload.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Preloading resource types %s' % ResourcesTypes.typeToStr(resType))
        locations = self.resLocations.get(resType)
        if locations is not None:
            for loc in locations:
                self.preloadResourceLocation(loc.name, [resType], False)


    def preloadResourceLocation(self, locName, resourceTypes = None, clearPreloadStore = False):
        '''
        Pre-loads all resources contained in the specified resource locations. You can also used the resType parameter
        to control what type of resources you want to be loaded.
        @param locName: The name of the resource location.
        @param resourceTypes: A constant that identifies the type of resources to preload. If it is None, then
        all resource types within this resource location will be considered.
        @param clearPreloadStore: If true, then the preload storage will be clear before proceeded with any
        further operations.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Preloading %s' % locName)
            
        if clearPreloadStore:
            self.preloadStore.clear()

        loc = self.locationsByName.get(locName)
        if loc is not None:

            # if the types to preload is omitted then set to load only the supported types of the resource location
            typesToPreload = resourceTypes
            if typesToPreload is None:
                typesToPreload = loc.getResourcesTypes()

            for resType in typesToPreload:
                resPaths = loc.listResources(resType, False)
                for filename in resPaths:
                    if self.log.isEnabledFor(logging.DEBUG):
                        self.log.debug('Preloading resource file %s' % filename)
                    res = self._loadInternal(resType, filename, locName, True)
                    if res is not None:                        
                        self._storePreloaded(res, res.fullPath, locName)


    def _loadInternal(self, resType, filename, locationName = None, preloading = False):
        '''
        Manages the actual loading of a resource given the resource filename and the resource location
        that contains it.

        @param resType: A constant that identifies the type of the resource.
        @param filename: The filename of the resource.
        @param locationName: The name of the resource location containing the resource. This is optional.
        @return: A pano.resources.Resource instance if preloading is True, the actual resource instance
        if preloading is False or None if the resource couldn't be found.
        '''

        self.requests += 1

        if locationName is not None:
            location = self.locationsByName.get(locationName)
        else:
            location = self.locateResource(resType, filename)
        if location is None:
            self.log.error('Failed to locate resource %s' % filename)
            return None

        fullPath = location.getResourceFullPath(filename)
        if fullPath is None:
            self.log.error('Failed to get full path to resource %s' % filename)
            return None

        # resource locations can be sticky
        if location.sticky:
            resource = self._getStickyResource(fullPath, resType)
            if resource is not None:
                if self.log.isEnabledFor(logging.DEBUG):
                    self.log.debug('Returning sticky resource %s' % fullPath)

                self.stickyLoads += 1
                if not preloading:
                    resource.requested = True
                return resource.data if not preloading else resource

        # if the location has a preload flag, then search first in the preload store
        if location.preload:
            resource = self._fetchPreloaded(fullPath, location.name)
            if resource is not None:
                self.preloadHits += 1
                if not preloading:
                    resource.requested = True
                return resource.data if not preloading else resource
            else:
                self.preloadMisses += 1

        # then search in our cache        
#        resource = self._cacheLookup(fullPath, location.name)
#        if resource is not None:
#            if self.log.isEnabledFor(logging.DEBUG):
#                self.log.debug('Returning cached instance of resource %s' % fullPath)
#            if not preloading:
#                resource.requested = True
#            return resource.data if not preloading else resource

        # finally load it from the resource location        
        if ResourcesTypes.isParsedResource(resType):
            # Convention: construct resource name from the basename of the filename and by dropping the extension.
            resName = os.path.basename(filename)
            extIndex = resName.rfind('.')
            if extIndex >= 0:
                resName = resName[:extIndex]

            resData = self._loadParsedResource(resType, resName, fullPath, True)            

        else:
            if ResourcesTypes.isPandaResource(resType):
                # for Panda resources we use the BaseLoader
                resName = filename
                try:
                    if resType == PanoConstants.RES_TYPE_MODELS:
                        resData = loader.loadModel(fullPath)

                    elif resType == PanoConstants.RES_TYPE_TEXTURES or resType == PanoConstants.RES_TYPE_VIDEOS:
                        resData = loader.loadTexture(fullPath)

                    elif resType == PanoConstants.RES_TYPE_MUSIC:
                        resData = loader.loadMusic(fullPath)

                    elif resType == PanoConstants.RES_TYPE_SFX:
                        resData = loader.loadSfx(fullPath)

                    elif resType == PanoConstants.RES_TYPE_SHADERS:
                        resData = Shader.load(fullPath)

                except Exception, e:
                    self.log.exception('Panda loader failed to load resource %s' % fullPath)                    
                    return None

            elif ResourcesTypes.isStreamResource(resType):
                # we consider character based and binary based streams
                # by handling stream resources in a special way we can perhaps provide more efficient
                # handling of streams, i.e. memory mapped files, compressed streams, decryption, etc.
                resName = filename                
                if resType == PanoConstants.RES_TYPE_SCRIPTS or resType == PanoConstants.RES_TYPE_TEXTS:
                    resData = self._loadCharacterStream(fullPath)
                else:
                    resData = self._loadBinaryStream(fullPath)

            if resData is None:
                self.log.error('Failed to load resource %s' % fullPath)
                return None

        resource = Resource(resName, resData, resType, fullPath, location.name)
        resource.sticky = location.sticky
        resource.preload = location.preload
        if not preloading:
            resource.requested = True

        # consider caching the resource
        if not resource.sticky and not resource.preload:
            self._cacheResource(fullPath, resource, location.name)

        elif resource.sticky:
            self._addStickyResource(fullPath, resource, location.name)
                
        # when we are preloading, return the Resource instance instead
        return resource.data if not preloading else resource


    def _loadParsedResource(self, resType, resName, filename, fullPath = False):
        '''
        Handles loading of all parsed resources such as .pointer, .node, .item, etc. resources.
        Since parsed resources are all text based, we assume that they are encoded in UTF-8 in order
        to support multilingual elements.

        @param resType:  The type of the resource.
        @param resName:  The name to give to the newly constructed resource.
        @param filename: The full path to the file that contains the resource.
        @param fullPath: Indicates if the resource has already been located and the input filename
                         can be used to load the resource.
        '''
        assert resType is not None and resType != PanoConstants.RES_TYPE_ALL, 'invalid resource type in loadGeneric'
        
        resPath = filename if fullPath else self.getResourceFullPath(resType, filename)
        if resPath is not None:

            with codecs.open(resPath, 'r', "utf-8") as istream:
                try:
                    # it is wrong to get resource streams in this way, in the future the resource location
                    # will be used to acquire a data stream
                    istream = codecs.open(resPath, 'r', "utf-8")
                    resObj = ResourcesTypes.constructParsedResource(resType, resName)
                    resource = self.parsers[resType].parse(resObj, istream)
                    return resource
                except Exception,e:
                    self.log.exception(e)

        else:
            raise ResourceNotFound(filename)


    def _loadCharacterStream(self, filename, encoding = "utf-8"):
        '''
        Loads the given filename as a stream of character, the decoding of the characters is based on the
        specified encoding which defaults to utf-8.
        @param filename: The full path to the file that contains the resource.
        @param encoding: The encoding to use for interpreting the characters.
        @return: A string object that has the file contents or None if loading failed.
        '''
        try:
            resPath = self.getResourceFullPath(PanoConstants.RES_TYPE_TEXTS, filename)
            with codecs.open(resPath, 'r', encoding) as istream:
                return istream.read()
        except Exception, e:
            self.log.exception(e)


    def _loadBinaryStream(self, filename):
        '''
        Loads the given filename as a stream of bytes.
        @param filename: The full path to the file that contains the resource.
        @return: A string object that has the file contents or None if loading failed.
        '''
        try:
            resPath = self.getResourceFullPath(PanoConstants.RES_TYPE_BINARIES, filename)
            with open(resPath, 'r') as istream:
                return istream.read()
        except Exception,e:
            self.log.exception(e)


    def _storePreloaded(self, res, filename, location):
        '''
        Stores a resource in the special storage allocated for preloaded
        resources.
        @param res: The loaded resource, a pano.resources.Resource instance.
        @param filename: The full path to the file that contains the resource.
        @param location: The name of the resource location containing the resource.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('adding pre-loaded resource %s of type %s' % (filename, ResourcesTypes.typeToStr(res.type)))

        perLocation = self.preloadStore.get(location)
        if perLocation is None:
            perLocation = {}
        perLocation[filename] = res
        self.preloadStore[location] = perLocation


    def _fetchPreloaded(self, filename, locationName):
        '''
        Looks up the resource in the special storage allocated for preloaded
        resources.
        Note: Once a resource that exists in the preload store gets requested
        it immediately leaves the store but get cached instead.

        @param filename: The full path to the file that contains the resource.
        @param locationName: The name of the resource location containing the resource.
        @return: A pano.resources.Resource instance or None if the resource couldn't be found.
        '''
        perLocation = self.preloadStore.get(locationName)
        if perLocation is not None:
            res = perLocation.get(filename)
            if res is not None:
                # detect NodePath who have released their models or other previously attached
                # resources. These are effectively invalid as they are useless, so pretend we
                # didn't fint them.
                if type(res) == NodePath and res.isEmpty():
                    if self.log.isEnabledFor(logging.INFO):
                        self.log.info('preloaded scenegraph resource was invalid, re-loading from file %s' % filename)
                    return None
                else:
                    # remove from preload but cache it
                    del perLocation[filename]
                    self._cacheResource(filename, res, locationName)
                    res.isRequested = True
                    return res
        else:
            return None
        

    def _cacheResource(self, filename, resource, locationName):
        '''
        @param filename: The full path to the file that contains the resource.
        @param resource: The loaded resource, a pano.resources.Resource instance.
        @param locationName: The name of the resource location containing the resource.
        '''
        self.cache[filename] = (resource, locationName)


    def _cacheLookup(self, filename, locationName):
        '''
        @param filename: The full path to the file that contains the resource.
        @param locationName: The name of the resource location containing the resource.
        @return: A pano.resources.Resource instance or None if the resource couldn't be found.
        '''
        if self.cache.has_key(filename):        
            res, locName = self.cache.get(filename)            
            if res is not None and locName == locationName:
                # detect NodePath who have released their models or other previously attached
                # resources. These are effectively invalid as they are useless, so pretend we
                # didn't fint them.
                if type(res.data) == NodePath and res.data.isEmpty():
                    if self.log.isEnabledFor(logging.INFO):
                        self.log.info('cached scenegraph resource was invalid, ignoring cached instance')
                    return None
                else:
                    return res
        else:
            return None


    def _addStickyResource(self, filename, resource, locationName):
        '''
        Adds a resource to the sticky list, i.e. in the list of resources that remain loaded throughout the lifetime
        of the game.
        @param filename: The full path to the file that contains the resource.
        @param res: The loaded resource, a pano.resources.Resource instance.
        @param locationName: The name of the resource location containing the resource.
        '''
        if self._getStickyResource(filename, locationName) is None:
            stList = self.stickyResources.get(filename)
            if stList is None:
                stList = []

            stList.append((resource, locationName))


    def _getStickyResource(self, filename, locationName):
        '''
        Returns the resource identified by the given filename, resource type and resource location
        from the sticky resources.
        @param filename: The full path to the file that contains the resource.
        @param locationName: The name of the resource location containing the resource.
        @return: A pano.resources.Resource instance or None if the resource couldn't be found.
        '''
        # first we get a list of resources with that name (could be many because
        # we support multiple uses of a name as long as the resources are in different
        # locations) and then try to find a match based on the location
        stickiesList = self.stickyResources.get(filename)
        if stickiesList is not None:
            for res, loc in stickiesList:
                if loc == locationName:
                    return res

