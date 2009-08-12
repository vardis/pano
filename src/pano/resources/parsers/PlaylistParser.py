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

import StringIO
import logging
from ConfigParser import *

from pano.constants import PanoConstants
from pano.errors.ParseException import ParseException

class PlaylistParser:
    
    TRACKS_SECTIONS = "tracks"
    OPTIONS_SECTIONS = "options"
    
    LOOP_OPTION = "loop"
    VOLUME_OPTION = "volume"
    SHUFFLE_OPTION = "shuffle"
    
    def __init__(self):
        self.log = logging.getLogger('pano.mplParser')
    
    def parse(self, playlist, fileContents):
                      
        try:
            cfg = SafeConfigParser()
            strFp = StringIO.StringIO(fileContents)
            cfg.readfp(strFp)
            
            trackOptions = cfg.options(PlaylistParser.TRACKS_SECTIONS)
            
            for i, opt in enumerate(trackOptions):
                track = cfg.get(PlaylistParser.TRACKS_SECTIONS, opt).split(',')
                playlist.addTrack(track[0].strip(), track[1].strip())
             
            if cfg.has_section(PlaylistParser.OPTIONS_SECTIONS):
                if cfg.has_option(PlaylistParser.OPTIONS_SECTIONS, PlaylistParser.LOOP_OPTION):
                        playlist.loop = cfg.getboolean(PlaylistParser.OPTIONS_SECTIONS, PlaylistParser.LOOP_OPTION)
                        
                if cfg.has_option(PlaylistParser.OPTIONS_SECTIONS, PlaylistParser.VOLUME_OPTION):
                        playlist.volume = cfg.getfloat(PlaylistParser.OPTIONS_SECTIONS, PlaylistParser.VOLUME_OPTION)
                        
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=playlist.getName() + '.mpl')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=playlist.getName() + '.mpl', args=(str(e)))
        
        else:
            return playlist
        