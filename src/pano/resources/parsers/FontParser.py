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
import StringIO
from ConfigParser import *

from pano.constants import PanoConstants
from pano.errors.ParseException import ParseException

class FontParser:
    def __init__(self):
        self.log = logging.getLogger('pano.fontParser')
    
    def parse(self, font, fileContents):
                      
        try:
            cfg = SafeConfigParser()
            strFp = StringIO.StringIO(fileContents)
            cfg.readfp(strFp)
            
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
        