import logging
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class PlaylistParser:
    
    TRACKS_SECTIONS = "tracks"
    OPTIONS_SECTIONS = "options"
    
    LOOP_OPTION = "loop"
    VOLUME_OPTION = "volume"
    SHUFFLE_OPTION = "shuffle"
    
    def __init__(self):
        self.log = logging.getLogger('pano.mplParser')
    
    def parse(self, playlist, istream):
                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
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
        