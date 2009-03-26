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


class MousePointer:
    """
    Properties for the mouse pointer. 
    """        

    def __init__(self, name = '', modelFile = None, enableAlpha = False, texture = None, scale = 1.0):
        self.__name = name
        self.modelFile = modelFile
        self.__texture = texture
        self.__enableAlpha = enableAlpha
        self.scale = scale
    
    def getName(self):
        return self.__name


    def getModelFile(self):
        return self.modelFile


    def getTexture(self):
        return self.__texture


    def getEnableAlpha(self):
        return self.__enableAlpha


    def setName(self, value):
        self.__name = value


    def setModelFile(self, value):
        self.modelFile = value


    def setTexture(self, value):
        self.__texture = value


    def getScale(self):
        return self.scale
    
    def setScale(self, scale):
        self.scale = scale

    def setEnableAlpha(self, value):
        self.__enableAlpha = value

    name = property(getName, setName, None, "The name of the mouse pointer, it should be unique")

    texture = property(getTexture, setTexture, None, "The filename of the texture to use ass a mouse pointer")

    enableAlpha = property(getEnableAlpha, setEnableAlpha, None, "True if the texture contain alpha information")
    
    