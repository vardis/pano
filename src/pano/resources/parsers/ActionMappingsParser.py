
import logging
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class ActionMappingsParser():
    
    def __init__(self):
        self.log = logging.getLogger('pano.mappingsParser')
    
    def parse(self, mappings, istream):
                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            options = cfg.options('mappings')
            for opt in options:
                val = cfg.get('mappings', opt)
            
                mappings.addMapping(opt, val)
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=mappings.getName() + '.mappings')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=mappings.getName() + '.mappings', args=(str(e)))
        
        else:
            return mappings