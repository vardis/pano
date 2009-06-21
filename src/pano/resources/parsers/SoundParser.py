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

from pano.constants import PanoConstants
from pano.errors.ParseException import ParseException
from pano.model.Sound import *


class SoundParser:
    
    SOUND_SECTION      = 'sound'
    SOUND_OPT_FILENAME = 'filename'
    SOUND_OPT_VOLUME   = 'volume'
    SOUND_OPT_BALANCE  = 'balance'    
    SOUND_OPT_RATE     = 'rate'
    SOUND_OPT_NODE     = 'node'
    SOUND_OPT_LOOP     = 'loop'
    SOUND_OPT_SUBS     = 'subtitles'

    POSITIONAL_SECTION = "positional"
    POSITIONAL_NODE     = "node"
    POSITIONAL_HOTSPOT  = "hotspot_pos"
    POSITIONAL_ABS      = "pos"

    CHORUS_SECTION      = "chorus_filter"
    REVERB_SECTION      = "reverb_filter"
    FLANGE_SECTION      = "flange_filter"
    ECHO_SECTION        = "echo_filter"
    DISTORTION_SECTION  = "distortion_filter"
    HIGH_PASS_SECTION   = "high_pass_filter"
    LOW_PASS_SECTION    = "low_pass_filter"
    COMPRESS_SECTION    = "compress_filter"
    PARAMEQ_SECTION     = "parameq_filter"
    PITCH_SHIFT_SECTION = "pitch_shift_filter"
    NORMALIZE_SECTION   = "normalize_filter"

    # note: the name of the configuration properties must match the names of the filter's class attributes
    propsPerFilter = {
        CHORUS_SECTION : (ChorusFilter, ['dryMix', 'wet1','wet2', 'wet3', 'delay','rate', 'depth', 'feedback']),
        REVERB_SECTION : (ReverbFilter, ['drymix','wetmix','room_size','damp','width']),
        FLANGE_SECTION : (FlangeFilter, ['drymix','wetmix','depth','rate']),
        ECHO_SECTION : (EchoFilter, ['drymix','wetmix','delay','decay_ration']),
        DISTORTION_SECTION : (DistortFilter, ['level']),
        HIGH_PASS_SECTION : (HighPassFilter, ['cutoff_freq','reasonance_q']),
        LOW_PASS_SECTION : (LowPassFilter, ['cutoff_freq','reasonance_q']),
        COMPRESS_SECTION : (CompressFilter, ['threshold','attack','release','gain']),
        PITCH_SHIFT_SECTION : (PitchShiftFilter, ['pitch','fft_size','overlap']),
        PARAMEQ_SECTION : (ParameqFilter, ['center_freq','bandwidth','gain']),
        NORMALIZE_SECTION : (NormalizeFilter, ['fade_time','threshold','max_amp'])
    }

    def __init__(self):
        self.log = logging.getLogger('pano.soundParser')
    
    def parse(self, sound, istream):
                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_FILENAME):
                sound.soundFile = cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_FILENAME)
            
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_VOLUME):
                sound.volume = cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_VOLUME)
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_BALANCE):
                sound.balance = cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_BALANCE)
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_RATE):
                sound.playRate = cfg.getfloat(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_RATE)
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_NODE):
                sound.node = cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_NODE)                        
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_SUBS):
                sound.subtitles = cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_SUBS)
                
            if cfg.has_option(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP):
                
                s = cfg.get(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP)
                if s.isalpha():
                    sound.loop = cfg.getboolean(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP)
                else:
                    sound.loop = cfg.getint(SoundParser.SOUND_SECTION, SoundParser.SOUND_OPT_LOOP)

            # positional options
            if cfg.has_option(SoundParser.POSITIONAL_SECTION, SoundParser.POSITIONAL_ABS):
                coords = cfg.get(SoundParser.POSITIONAL_SECTION, SoundParser.POSITIONAL_ABS)
                x, y, z = coords.split(' ')
                sound.positional = Sound.POS_Absolute
                sound.node = (x, y, z)

            elif cfg.has_option(SoundParser.POSITIONAL_SECTION, SoundParser.POSITIONAL_HOTSPOT):
                sound.positional = Sound.POS_Hotspot
                sound.node = cfg.get(SoundParser.POSITIONAL_SECTION, SoundParser.POSITIONAL_HOTSPOT)

            elif cfg.has_option(SoundParser.POSITIONAL_SECTION, SoundParser.POSITIONAL_NODE):
                sound.positional = Sound.POS_None
                sound.node = cfg.get(SoundParser.POSITIONAL_SECTION, SoundParser.POSITIONAL_NODE)

            # read filters
            for section, (clazz, p) in SoundParser.propsPerFilter.items():
                if cfg.has_section(section):
                    f = clazz()
                    for attr in p:
                        if cfg.has_option(section, attr):
                            setattr(f, attr, cfg.getfloat(section, attr))

                    sound.setFilter(f)
                
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=sound.getName() + '.sound')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=sound.getName() + '.sound', args=(str(e)))
        
        else:
            return sound
    