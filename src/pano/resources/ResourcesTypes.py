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

from pano.constants             import PanoConstants
from pano.model.Font            import Font
from pano.model.Node            import Node
from pano.model.Sound           import Sound
from pano.model.MousePointer    import MousePointer
from pano.model.LangFile        import LangFile
from pano.model.Sprite          import Sprite
from pano.model.Playlist        import Playlist
from pano.model.ActionMappings  import ActionMappings
from pano.model.InventoryItem   import InventoryItem
from pano.model.HotspotsMaps    import QuadTreeMap
from pano.model.HotspotsMaps    import ImageMap

class ResourcesTypes:
    """
    A registry of all supported resource types.
    """
    resTypesExtensions = { 
            PanoConstants.RES_TYPE_NODES : ('.node'),
            PanoConstants.RES_TYPE_MODELS : ('.egg', '.egg.pz', '.bam' ),
            PanoConstants.RES_TYPE_TEXTURES : ('.jpg', '.bmp', '.tga', '.tif', '.png', '.dds'),
            PanoConstants.RES_TYPE_FONTS : ('.font'),
            PanoConstants.RES_TYPE_SOUNDS_DEFS : ('.sound'),
            PanoConstants.RES_TYPE_SFX : ('.wav', '.ogg', '.midi', '.mp3', '.avi', '.mpg', '.mpeg', '.ogm'),
            PanoConstants.RES_TYPE_MUSIC : ('.wav', '.ogg', '.midi', '.mp3', '.avi', '.mpg', '.mpeg', '.ogm'),
            PanoConstants.RES_TYPE_POINTERS : ('.pointer'),
            PanoConstants.RES_TYPE_LANGS : ('.lang'),
            PanoConstants.RES_TYPE_SPRITES : ('.spr'),
            PanoConstants.RES_TYPE_PLAYLISTS : ('.mpl'),
            PanoConstants.RES_TYPE_VIDEOS : ('.wmv', '.flv', '.asf', '.avi', '.mpg', '.ogg', '.ogm', '.mov'),
            PanoConstants.RES_TYPE_MAPPINGS : ('.mappings'),
            PanoConstants.RES_TYPE_ITEMS : ('.item'),
            PanoConstants.RES_TYPE_SCRIPTS : ('.py'),
            PanoConstants.RES_TYPE_TEXTS : ('.txt', '.py'),
            PanoConstants.RES_TYPE_BINARIES : ('.bin'),
            PanoConstants.RES_TYPE_SHADERS : ('.sha'),
            PanoConstants.RES_TYPE_HMAPS : ('.qmap', '.imap'),            
            PanoConstants.RES_TYPE_IMAGES : ('.jpg', '.bmp', '.tga', '.tif', '.png', '.dds')
    }
    
    resTypesNames = { 
            PanoConstants.RES_TYPE_NODES : 'Node',
            PanoConstants.RES_TYPE_MODELS : 'Model',
            PanoConstants.RES_TYPE_TEXTURES : 'Texture',
            PanoConstants.RES_TYPE_FONTS : 'Font',
            PanoConstants.RES_TYPE_SOUNDS_DEFS : 'Sound Definition',
            PanoConstants.RES_TYPE_SFX : 'Sound file',
            PanoConstants.RES_TYPE_MUSIC : 'Music file',
            PanoConstants.RES_TYPE_POINTERS : 'Pointer',
            PanoConstants.RES_TYPE_LANGS : 'Language file',
            PanoConstants.RES_TYPE_SPRITES : 'Sprite',
            PanoConstants.RES_TYPE_PLAYLISTS : 'Music Playlist',
            PanoConstants.RES_TYPE_VIDEOS : 'Video',
            PanoConstants.RES_TYPE_MAPPINGS : 'Input mappings',
            PanoConstants.RES_TYPE_ITEMS : 'Item',
            PanoConstants.RES_TYPE_SCRIPTS : 'Script',
            PanoConstants.RES_TYPE_TEXTS : 'Text file',
            PanoConstants.RES_TYPE_BINARIES : 'Binary file',
            PanoConstants.RES_TYPE_SHADERS : 'Shader',
            PanoConstants.RES_TYPE_HMAPS : "Hotspots map",            
            PanoConstants.RES_TYPE_IMAGES : "Image"
    
    }

    def listAllTypes():
        return ResourcesTypes.resTypesNames.keys()

    def getExtensions(resType):
        """
        Returns a list of file extensions that are supported for the specified
        resource type. e.g. if resType specifies textures then the returned list
        could be ('.jpg', '.bmp', 'tga')
        @param resType: A constant that identifies the resource type.
        """
        if ResourcesTypes.resTypesExtensions.has_key(resType):
            return list(ResourcesTypes.resTypesExtensions[resType])
        elif resType == PanoConstants.RES_TYPE_ALL:
            all = []
            for val in ResourcesTypes.resTypesExtensions.values():
                all.append(list(val))
            return all
        else:
            return None
        
    def isExtensionOfType(extension, resType):
        '''
        @param extension: The filename extension
        @param resType: A constant that identifies the resource type.
        '''
        if ResourcesTypes.resTypesExtensions.has_key(resType):
            exts = ResourcesTypes.resTypesExtensions[resType]
            return extension in exts
        else:
            return False

    def isParsedResource(resType):
        '''
        @param resType: A constant that identifies the resource type.
        '''
        return resType in (
            PanoConstants.RES_TYPE_NODES,                        
            PanoConstants.RES_TYPE_FONTS,
            PanoConstants.RES_TYPE_SOUNDS_DEFS,            
            PanoConstants.RES_TYPE_POINTERS,
            PanoConstants.RES_TYPE_LANGS,
            PanoConstants.RES_TYPE_SPRITES,
            PanoConstants.RES_TYPE_PLAYLISTS,            
            PanoConstants.RES_TYPE_MAPPINGS,
            PanoConstants.RES_TYPE_ITEMS        
                           )
        
    def isStreamResource(resType):
        '''
        @param resType: A constant that identifies the resource type.
        '''
        return resType in (
            PanoConstants.RES_TYPE_SCRIPTS,                                    
            PanoConstants.RES_TYPE_TEXTS,
            PanoConstants.RES_TYPE_BINARIES       
                           )
        
    def isPandaResource(resType):
        '''
        @param resType: A constant that identifies the resource type.
        '''
        return resType in (                                
            PanoConstants.RES_TYPE_MODELS,
            PanoConstants.RES_TYPE_TEXTURES,            
            PanoConstants.RES_TYPE_SFX,
            PanoConstants.RES_TYPE_MUSIC,
            PanoConstants.RES_TYPE_VIDEOS,
            PanoConstants.RES_TYPE_SHADERS,
            PanoConstants.RES_TYPE_IMAGES       
                           )
        
    def isOpaqueResource(resType):
        '''
        Opaque resources provide the following methods for reading and writting their contents:
            read(fileObject)  - reads from a file like object, 
            readStream(str)   - reads from a string stream, 
            write(fileObject) - write to a file like object, 
            str writeStream() - writes to a string stream
            
        @param resType: A constant that identifies the resource type.
        '''
        return resType in (
            PanoConstants.RES_TYPE_HMAPS,       
                           )
                
    def constructParsedResource(resType, name):
        '''
        Constructs a resource object of the given type and name.
        Note that the resource type must correspond to a parsed resource.
        
        @param resType: A constant that identifies the resource type.
        @param name: The name to be assigned to the constructed resource. 
        '''
        constructors = {
                        PanoConstants.RES_TYPE_NODES : Node,                        
                        PanoConstants.RES_TYPE_FONTS : Font,
                        PanoConstants.RES_TYPE_SOUNDS_DEFS : Sound,                                    
                        PanoConstants.RES_TYPE_POINTERS : MousePointer,
                        PanoConstants.RES_TYPE_LANGS : LangFile,
                        PanoConstants.RES_TYPE_SPRITES : Sprite,
                        PanoConstants.RES_TYPE_PLAYLISTS : Playlist,
                        PanoConstants.RES_TYPE_MAPPINGS : ActionMappings,
                        PanoConstants.RES_TYPE_ITEMS : InventoryItem
                        }
        
        assert constructors.has_key(resType)        
        return constructors[resType](name)

    def constructOpaqueResource(resType, name, filename):
        if resType == PanoConstants.RES_TYPE_HMAPS:  
            if filename.endswith('qmap'):          
                return QuadTreeMap(name)
            elif filename.endswith('imap'):
                return ImageMap(name)

    def typeToStr(resType):
        '''
        Returns a descriptive name for the given resource type.
        @param resType: A constant that identifies the resource type.
        '''
        return ResourcesTypes.resTypesNames.get(resType)
            
    listAllTypes = staticmethod(listAllTypes)
    typeToStr = staticmethod(typeToStr)
    getExtensions = staticmethod(getExtensions)
    isExtensionOfType = staticmethod(isExtensionOfType)
    isPandaResource = staticmethod(isPandaResource)
    isStreamResource = staticmethod(isStreamResource)
    isParsedResource = staticmethod(isParsedResource)
    isOpaqueResource = staticmethod(isOpaqueResource)
    constructParsedResource = staticmethod(constructParsedResource)
    constructOpaqueResource = staticmethod(constructOpaqueResource)
        
