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
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class SpriteParser:
    
    SPRITE_SECTION      = 'sprite'
    SPRITE_OPT_EGGFILE  = 'egg_file'
    SPRITE_OPT_IMAGE  = 'image'
    SPRITE_OPT_FPS      = 'frame_rate'
    SPRITE_OPT_WIDTH    = 'width'
    SPRITE_OPT_HEIGHT   = 'height'
    SPRITE_OPT_VIDEO    = 'video_file'
    SPRITE_OPT_AUDIO    = 'audio_file'
    
    def __init__(self):
        self.log = logging.getLogger('pano.spriteParser')
        
    def parse(self, sprite, istream):
                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_EGGFILE):
                sprite.setEggFile(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_EGGFILE))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_IMAGE):
                sprite.setImage(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_IMAGE))
            
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_FPS):
                sprite.setFrameRate(cfg.getfloat(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_FPS))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_WIDTH):
                sprite.setWidth(cfg.getint(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_WIDTH))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_HEIGHT):
                sprite.setHeight(cfg.getint(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_HEIGHT))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_VIDEO):
                sprite.setVideo(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_VIDEO))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_AUDIO):
                sprite.setAudio(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_AUDIO))
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=sprite.getName() + '.spr')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=sprite.getName() + '.spr', args=(str(e)))
        
        else:
            return sprite
        