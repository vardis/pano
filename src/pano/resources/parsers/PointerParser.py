from ConfigParser import SafeConfigParser

from model.MousePointer import MousePointer

class PointerParser:    
    """
    Parses .pointer files and returns an instance of the pointer class or None 
    if the parsing failed.
    pointer files contain key = value lines similar to .ini files and contain section headers
    again in similar fashion. For pointer files there must be only one section header named 'pointer'.
    The following keys are supported for pointers:
    a) egg_file: if present it specifies the 3D model to use as a cursor. It is useful to create animated
    pointers by using the TexturedCard class. String value that specifies the model name.
    b) texture: the texture to use as a static mouse pointer. String value that specifies the texture name.
    c) enable_alpha: if true then the texture is assumed to contain alpha information and the alpha attribute
    should be enabled. Boolean value that specifies if alpha should be enabled.
    """
    
    EGG_FILE_OPTION = 'egg_file'
    TEXTURE_OPTION = 'texture'
    ALPHA_OPTION = 'enable_alpha'
    
    def __init__(self):
        pass
    
    def parse(self, istream):
        """
        Parses a .pointer file whose contents will be read by the given input stream
        """
        cfg = SafeConfigParser()
        
#        try:
        cfg.readfp(istream)
        section = cfg.sections()[0]
        assert section is not None and section == 'Pointer', 'pointer file must contain the "Pointer" section header'
        
        pointer = MousePointer()
        if cfg.has_option(section, PointerParser.EGG_FILE_OPTION):
            pointer.setEggFile(cfg.get(section, PointerParser.EGG_FILE_OPTION))
            
        if cfg.has_option(section, PointerParser.TEXTURE_OPTION):
            pointer.setTexture(cfg.get(section, PointerParser.TEXTURE_OPTION))
        
        if cfg.has_option(section, PointerParser.ALPHA_OPTION):
            pointer.setEnableAlpha(cfg.getboolean(section, PointerParser.ALPHA_OPTION))
        
        assert pointer.getEggFile() is not None or pointer.getTexture() is not None, 'either an egg file or a texture file must be specified for the pointer'
        
        return pointer
            
#        except:
#            print 'error while parsing pointer file'
        
        