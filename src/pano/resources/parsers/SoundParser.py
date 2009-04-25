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
from errors.ParseException import ParseException

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
    