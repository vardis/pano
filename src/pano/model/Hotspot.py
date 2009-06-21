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


class Hotspot(object):
    """
    Represents the model of a game hotspot. A hotspot is a rectangular area on the
    panoramic view that can interact with the user through the mouse.
    Each hotspot defines the face of the cubemap on which it belongs, the coordinates
    of the top left corner of its rectangular area and the width and height of its area.
    """
    
    def __init__(self, name='', description='', face=None, x=0, y = 0, width = 0, height=0, action=None):
        self.name = name
        self.description = description
        self.face = face
        
        # upper left corner coordinates
        self.xo = float(x)
        self.yo = float(y)
        
        # lower right corner coordinates
        self.xe = float(x + width)
        self.ye = float(y + height)
        
        self.width = width
        self.height = height
        self.action = action
        self.actionArgs = ()
        self.cursor = None
        self.active = True
        self.sprite = None
        self.itemInteractive = False        

    def getXo(self):
        return self.xo
    
    def setXo(self, value):
        self.xo = float(value)        
        self.setXe(value + self.width)

    def getYo(self):
        return self.yo

    def setYo(self, value):
        self.yo = float(value)
        self.setYe(value + self.height)

    def getXe(self):
        return self.xe

    def setXe(self, value):
        self.xe = float(value)
        self.width = self.xe = self.xo

    def getYe(self):
        return self.ye

    def setYe(self, value):
        self.ye = float(value)
        self.height= self.ye = self.yo
        
    def getWidth(self):
        return self.width

    def setWidth(self, value):
        self.width = value
        self.xe = self.xo + self.width

    def getHeight(self):
        return self.height

    def setHeight(self, value):
        self.height = value
        self.ye = self.yo + self.height

    def hasAction(self):
        return self.action is not None
        
    