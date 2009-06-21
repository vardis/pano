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

import ConfigParser
from ConfigParser import SafeConfigParser

from pano.constants import PanoConstants
from pano.errors.ParseException import ParseException
from pano.model.Node import Node
from pano.model.Hotspot import Hotspot

class NodeParser:
    
    NODE_SECTION        = 'Node'
    NODE_OPT_DESC       = 'description'
    NODE_OPT_CUBEMAP    = 'cubemap'
    NODE_OPT_IMAGE      = 'image'
    NODE_OPT_BGCOLOR    = 'bg_color'
    NODE_OPT_EXTENSION  = 'extension'
    NODE_OPT_SCRIPT     = 'script'
    NODE_OPT_LOOKAT     = 'lookat'
    NODE_OPT_PARENT     = 'parent2d'
    NODE_OPT_PLAYLIST   = 'music_playlist'
    
    HOTSPOT_OPT_LOOKTEXT     = 'look_text'
    HOTSPOT_OPT_FACE         = 'face'    
    HOTSPOT_OPT_XO           = 'xo'
    HOTSPOT_OPT_YO           = 'yo'
    HOTSPOT_OPT_WIDTH        = 'width'
    HOTSPOT_OPT_HEIGHT       = 'height'
    HOTSPOT_OPT_XE           = 'xe'
    HOTSPOT_OPT_YE           = 'ye'
    HOTSPOT_OPT_ACTIVE       = 'active'
    HOTSPOT_OPT_CURSOR       = 'cursor'
    HOTSPOT_OPT_ACTION       = 'action'
    HOTSPOT_OPT_ACTIONARGS   = 'action_args'
    HOTSPOT_OPT_SPRITE       = 'sprite'
    HOTSPOT_OPT_ITEMINTERACT = 'interacts_items'
    
    
    def __init__(self):
        self.__facesCodes = {
                             'front' : PanoConstants.CBM_FRONT_FACE,
                             'back' : PanoConstants.CBM_BACK_FACE,
                             'left' : PanoConstants.CBM_LEFT_FACE,
                             'right' : PanoConstants.CBM_RIGHT_FACE,
                             'top' : PanoConstants.CBM_TOP_FACE,
                             'bottom' : PanoConstants.CBM_BOTTOM_FACE
        }
    
    def parse(self, node, istream):
        """
        Parses a .pointer file whose contents will be read by the given input stream
        """
        cfg = SafeConfigParser()
        
        try:
            cfg.readfp(istream)
            
            assert cfg.has_section(NodeParser.NODE_SECTION), 'Invalid .node file, a node section hasn''t been defined'            
            
            # read node's options
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_DESC):
                node.description = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_DESC)
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_CUBEMAP):
                node.cubemap = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_CUBEMAP)
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_IMAGE):
                node.image = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_IMAGE)
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_BGCOLOR):
                bgColorStr = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_BGCOLOR)    
                node.bgColor = [x.strip() for x in bgColorStr.split(',')]                        
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_SCRIPT):
                node.scriptName = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_SCRIPT)
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_LOOKAT):
                node.lookat = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_LOOKAT)
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_EXTENSION):
                node.extension = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_EXTENSION)

            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_PARENT):
                parent = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_PARENT)
                if parent == 'render2d':
                    node.parent2d = Node.PT_Render2D
                elif parent == 'aspect2d':
                    node.parent2d = Node.PT_Aspect2D
                else:
                    node.parent2d = None

            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_PLAYLIST):
                node.musicPlaylist = cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_PLAYLIST)
        
            for s in cfg.sections():
                if s.startswith('hotspot_'):
                    hp = Hotspot(name = s[8:])
                    
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_FACE):
                        face = cfg.get(s, NodeParser.HOTSPOT_OPT_FACE)
                        assert self.__facesCodes.has_key(face), 'invalid face name: ' + face                    
                        hp.face = self.__facesCodes[face]
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_LOOKTEXT):
                        hp.description = cfg.get(s, NodeParser.HOTSPOT_OPT_LOOKTEXT)
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_XO):
                        hp.setXo(cfg.getint(s, NodeParser.HOTSPOT_OPT_XO))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_YO):
                        hp.setYo(cfg.getint(s, NodeParser.HOTSPOT_OPT_YO))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_XE):
                        hp.setXe(cfg.getint(s, NodeParser.HOTSPOT_OPT_XE))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_YE):
                        hp.setYe(cfg.getint(s, NodeParser.HOTSPOT_OPT_YE))
                                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_WIDTH):
                        hp.setWidth(cfg.getint(s, NodeParser.HOTSPOT_OPT_WIDTH))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_HEIGHT):
                        hp.setHeight(cfg.getint(s, NodeParser.HOTSPOT_OPT_HEIGHT))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_ACTION):
                        actionStr = cfg.get(s, NodeParser.HOTSPOT_OPT_ACTION)
                        argList = [x.strip() for x in actionStr.split(',')]
                        hp.action = argList.pop(0)
                        hp.actionArgs = argList                            
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_ACTIONARGS):
                        hp.actionArgs = cfg.get(s, NodeParser.HOTSPOT_OPT_ACTIONARGS)
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_ACTIVE):
                        hp.active = cfg.getboolean(s, NodeParser.HOTSPOT_OPT_ACTIVE)
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_CURSOR):
                        hp.cursor = cfg.get(s, NodeParser.HOTSPOT_OPT_CURSOR)
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_SPRITE):
                        hp.sprite = cfg.get(s, NodeParser.HOTSPOT_OPT_SPRITE)
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_ITEMINTERACT):
                        hp.itemInteractive = cfg.getboolean(s, NodeParser.HOTSPOT_OPT_ITEMINTERACT) 
                        
                    node.addHotspot(hp)
                
        except (ConfigParser.MissingSectionHeaderError, ConfigParser.ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=node.name + '.node')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=node.name + '.node', args=(str(e)))
        
        else:
            return node
                    
                
                
            
        
         
         

