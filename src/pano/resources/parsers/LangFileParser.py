import logging
from ConfigParser import *

from constants import PanoConstants
from pano.exceptions.ParseException import ParseException

class LangFileParser():
    
    def __init__(self):
        self.log = logging.getLogger('pano.langParser')
    
    def parse(self, langFile, istream):
                
        name = langFile.getName()
        langFile.setLanguage(name[name.index('_')+1:])
        print 'set language to ' , langFile.getLanguage()
        cfg = SafeConfigParser()        
        try:
            cfg.readfp(istream)
            
            options = cfg.options('labels')
            for opt in options:
                val = cfg.get('labels', opt)
                langFile[opt] = val                 
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=langFile.getName() + '.lang')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=langFile.getName() + '.lang', args=(str(e)))
        
        else:
            return langFile
        