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
from pano.exceptions.ParseException import ParseException

class InventoryItemParser:
    """
    Parses .item resources which describe the properties of inventory items.
    """
    
    # constants for the section and options names
    ITEM_SECTION = "item"
    SOUND_OPTION = "sound"
    DESCRIPTION_OPTION = "description"
    IMAGE_OPTION = "image"
    SELECTED_IMAGE_OPTION = "selected_image"
    COUNT_OPTION = "count"
    MAX_COUNT_OPTION = "max_count"
    
    def __init__(self):
        self.log = logging.getLogger('pano.itemParser')

    def parse(self, item, istream):                      
        try:
            cfg = SafeConfigParser()
            cfg.readfp(istream)
            
            if cfg.has_option(self.ITEM_SECTION, self.SOUND_OPTION):
                item.setSound(cfg.get(self.ITEM_SECTION, self.SOUND_OPTION))
                
            if cfg.has_option(self.ITEM_SECTION, self.DESCRIPTION_OPTION):
                item.setDescription(cfg.get(self.ITEM_SECTION, self.DESCRIPTION_OPTION))
                
            if cfg.has_option(self.ITEM_SECTION, self.IMAGE_OPTION):
                item.setImage(cfg.get(self.ITEM_SECTION, self.IMAGE_OPTION))
                
            if cfg.has_option(self.ITEM_SECTION, self.SELECTED_IMAGE_OPTION):
                item.setSelectedImage(cfg.get(self.ITEM_SECTION, self.SELECTED_IMAGE_OPTION))
                
            if cfg.has_option(self.ITEM_SECTION, self.COUNT_OPTION):
                item.setCount(cfg.getint(self.ITEM_SECTION, self.COUNT_OPTION))
                
            if cfg.has_option(self.ITEM_SECTION, self.MAX_COUNT_OPTION):
                item.setMaxCount(cfg.getint(self.ITEM_SECTION, self.MAX_COUNT_OPTION))
                
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=item.getName() + '.item')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=item.getName() + '.item', args=(str(e)))
        
        else:
            return item
        