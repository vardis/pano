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

class LangFileParser():
    
    def __init__(self):
        self.log = logging.getLogger('pano.langParser')
    
    def parse(self, langFile, istream):
                
        name = langFile.getName()
        langFile.setLanguage(name[name.index('_')+1:])
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
        