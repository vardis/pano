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

from ConfigParser import SafeConfigParser

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException
from model.Node import Node
from model.Hotspot import Hotspot

class NodeParser:
    
    NODE_SECTION     = 'Node'
    NODE_OPT_DESC    = 'description'
    NODE_OPT_CUBEMAP = 'cubemap'
    NODE_OPT_IMAGE   = 'image'
    NODE_OPT_SCRIPT  = 'script'
    NODE_OPT_LOOKAT  = 'lookat'
    
    HOTSPOT_OPT_LOOKTEXT    = 'look_text'
    HOTSPOT_OPT_FACE        = 'face'    
    HOTSPOT_OPT_XO          = 'xo'
    HOTSPOT_OPT_YO          = 'yo'
    HOTSPOT_OPT_WIDTH       = 'width'
    HOTSPOT_OPT_HEIGHT      = 'height'
    HOTSPOT_OPT_XE          = 'xe'
    HOTSPOT_OPT_YE          = 'ye'
    HOTSPOT_OPT_ACTIVE      = 'active'
    HOTSPOT_OPT_CURSOR      = 'cursor'
    HOTSPOT_OPT_ACTION      = 'action'
    HOTSPOT_OPT_ACTIONARGS  = 'action_args'
    HOTSPOT_OPT_SPRITE      = 'sprite'
    
    
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
                node.setDescription(cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_DESC))
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_CUBEMAP):
                node.setCubemap(cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_CUBEMAP))
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_IMAGE):
                node.setImage(cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_IMAGE))
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_SCRIPT):
                node.setScriptName(cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_SCRIPT))
                
            if cfg.has_option(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_LOOKAT):
                node.setLookAt(cfg.get(NodeParser.NODE_SECTION, NodeParser.NODE_OPT_LOOKAT))
                
            for s in cfg.sections():
                if s.startswith('hotspot_'):
                    hp = Hotspot(name = s[8:])
                    
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_FACE):
                        face = cfg.get(s, NodeParser.HOTSPOT_OPT_FACE)
                        assert self.__facesCodes.has_key(face), 'invalid face name: ' + face                    
                        hp.setFace(self.__facesCodes[face])
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_LOOKTEXT):
                        hp.setDescription(cfg.get(s, NodeParser.HOTSPOT_OPT_LOOKTEXT))
                        
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
                        hp.setAction(cfg.get(s, NodeParser.HOTSPOT_OPT_ACTION))                            
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_ACTIONARGS):
                        hp.setActionArgs(cfg.get(s, NodeParser.HOTSPOT_OPT_ACTIONARGS))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_ACTIVE):
                        hp.setActive(cfg.getboolean(s, NodeParser.HOTSPOT_OPT_ACTIVE))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_CURSOR):
                        hp.setCursor(cfg.get(s, NodeParser.HOTSPOT_OPT_CURSOR))
                        
                    if cfg.has_option(s, NodeParser.HOTSPOT_OPT_SPRITE):
                        hp.setSprite(cfg.get(s, NodeParser.HOTSPOT_OPT_SPRITE))
                        
                    node.addHotspot(hp)
                
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=node.getName() + '.node')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=node.getName() + '.node', args=(str(e)))
        
        else:
            return node
                    
                
                
            
        
         
         

