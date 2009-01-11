import logging
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class FontParser:
    def __init__(self):
        self.log = logging.getLogger('pano.fontParser')
    
    def parse(self, font, istream):
                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            options = cfg.options('font')
            for opt in options:
                val = cfg.get('font', opt)
            
                if not(opt.startswith('locale_') and len(opt) >= 9):
                    raise ParseException(error='error.parse.invalidOption', resFile=font + '.font', args=(opt))
                
                language = opt[7:]                
                font.addLocalization(language, val) 
                
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=font.getName() + '.font')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=font.getName() + '.font', args=(str(e)))
        
        else:
            return font
        