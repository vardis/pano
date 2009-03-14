import logging
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class SoundParser:
    
    SOUND_SECTION      = 'sound'
    SOUND_OPT_FILENAME = 'filename'
    SOUND_OPT_VOLUME   = 'volume'
    SOUND_OPT_BALANCE  = 'balance'
    SOUND_OPT_CUTOFF   = 'cut_off'
    SOUND_OPT_RATE     = 'rate'
    SOUND_OPT_NODE     = 'node'
    SOUND_OPT_LOOP     = 'loop'
    SOUND_OPT_SUBS     = 'subtitles'
    
    def __init__(self):
        self.log = logging.getLogger('pano.soundParser')
    
    def parse(self, sound, istream):
                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_FILENAME):
                sound.setSoundFile(cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_FILENAME))
            
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_VOLUME):
                sound.setVolume(cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_VOLUME))
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_BALANCE):
                sound.setBalance(cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_BALANCE))
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_CUTOFF):
                sound.setCutOff(cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_CUTOFF))
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_RATE):
                sound.setPlayRate(cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_RATE))
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_NODE):
                sound.setNode(cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_NODE))                        
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_SUBS):
                sound.setSubtitles(cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_SUBS))
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP):
                
                s = cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP)
                if s.isalpha():
                    sound.setLoop(cfg.getboolean(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP))
                else:
                    sound.setLoop(cfg.getint(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP))
                
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=sound.getName() + '.sound')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=sound.getName() + '.sound', args=(str(e)))
        
        else:
            return sound
    