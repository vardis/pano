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
        