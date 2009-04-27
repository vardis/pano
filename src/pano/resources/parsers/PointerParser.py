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

from ConfigParser import SafeConfigParser

from pano.exceptions.ParseException import ParseException
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
    
    MODEL_FILE_OPTION = 'model_file'
    TEXTURE_OPTION = 'texture'
    ALPHA_OPTION = 'enable_alpha'
    SCALE_OPTION = 'scale'
    
    def __init__(self):
        pass
    
    def parse(self, pointer, istream):
        """
        Parses a .pointer file whose contents will be read by the given input stream
        """
        cfg = SafeConfigParser()
        
        try:
            cfg.readfp(istream)
            section = cfg.sections()[0]
            assert section is not None and section == 'Pointer', 'pointer file must contain the "Pointer" section header'
                    
            if cfg.has_option(section, PointerParser.MODEL_FILE_OPTION):
                pointer.setModelFile(cfg.get(section, PointerParser.MODEL_FILE_OPTION))
                
            if cfg.has_option(section, PointerParser.TEXTURE_OPTION):
                pointer.setTexture(cfg.get(section, PointerParser.TEXTURE_OPTION))
            
            if cfg.has_option(section, PointerParser.ALPHA_OPTION):
                pointer.setEnableAlpha(cfg.getboolean(section, PointerParser.ALPHA_OPTION))
                
            if cfg.has_option(section, PointerParser.SCALE_OPTION):
                pointer.setScale(cfg.getfloat(section, PointerParser.SCALE_OPTION))
            
            assert pointer.getModelFile() is not None or pointer.getTexture() is not None, 'either an egg file or a texture file must be specified for the pointer'
                
            
        except (MissingSectionHeaderError, ParsingError):
            raise ParseException(error='error.parse.invalid', resFile=pointer.getName() + '.pointer')
        
        except IOError, e:
            raise ParseException(error='error.parse.io', resFile=pointer.getName() + '.pointer', args=(str(e)))
        
        else:
            return pointer
        