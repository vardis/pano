import logging
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class SpriteParser:
    
    SPRITE_SECTION      = 'sprite'
    SPRITE_OPT_EGGFILE  = 'egg_file'
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
            
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_FPS):
                sprite.setFrameRate(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_FPS))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_WIDTH):
                sprite.setWidth(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_WIDTH))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_HEIGHT):
                sprite.setHeight(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_HEIGHT))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_VIDEO):
                sprite.setVideo(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_VIDEO))
                
            if cfg.has_option(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_AUDIO):
                sprite.setAudio(cfg.get(SpriteParser.SPRITE_SECTION, SpriteParser.SPRITE_OPT_AUDIO))
            
            assert sprite.getEggFile() is not None or sprite.getVideo() is not None, 'No sprite image source has been specified'                     
                
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=sprite.getName() + '.spr')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=sprite.getName() + '.spr', args=(str(e)))
        
        else:
            return sprite
        