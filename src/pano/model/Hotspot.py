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
        self.__name = name
        self.__description = description
        self.__face = face
        
        # upper left corner coordinates
        self.__xo = float(x)
        self.__yo = float(y)
        
        # lower right corner coordinates
        self.__xe = float(x + width)
        self.__ye = float(y + height)
        
        self.__width = width
        self.__height = height
        self.__action = action
        self.__actionArgs = ()
        self.__cursor = None
        self.__active = True
        self.__sprite = None
        self.itemInteractive = False        

    def getName(self):
        return self.__name


    def getDescription(self):
        return self.__description


    def getFace(self):
        return self.__face


    def getXo(self):
        return self.__xo


    def getYo(self):
        return self.__yo


    def getXe(self):
        return self.__xe


    def getYe(self):
        return self.__ye


    def getWidth(self):
        return self.__width


    def getHeight(self):
        return self.__height


    def getAction(self):
        return self.__action
    
    def hasAction(self):
        return self.__action is not None

    def getActionArgs(self):
        return self.__actionArgs


    def setName(self, value):
        self.__name = value


    def setDescription(self, value):
        self.__description = value


    def setFace(self, value):
        self.__face = value


    def setXo(self, value):
        self.__xo = float(value)        
        self.setXe(value + self.__width)

    def setYo(self, value):
        self.__yo = float(value)
        self.setYe(value + self.__height)

    def setXe(self, value):
        self.__xe = float(value)
        self.__width = self.__xe = self.__xo


    def setYe(self, value):
        self.__ye = float(value)
        self.__height= self.__ye = self.__yo
        

    def setWidth(self, value):
        self.__width = value
        self.__xe = self.__xo + self.__width


    def setHeight(self, value):
        self.__height = value
        self.__ye = self.__yo + self.__height


    def setAction(self, value):
        self.__action = value


    def setActionArgs(self, value):
        self.__actionArgs = value


    def getCursor(self):
        return self.__cursor


    def isActive(self):
        return self.__active


    def getSprite(self):
        return self.__sprite


    def setCursor(self, value):
        self.__cursor = value


    def setActive(self, value):
        self.__active = value


    def setSprite(self, value):
        self.__sprite = value

    def isItemInteractive(self):
       return self.itemInteractive

    def setItemInteractive(self, flag):
       self.itemInteractive = flag

    cursor = property(getCursor, setCursor, None, "Cursor's Docstring")

    active = property(isActive, setActive, None, "Active's Docstring")

    sprite = property(getSprite, setSprite, None, "Sprite's Docstring")

    name = property(getName, setName, None, "Name's Docstring")

    description = property(getDescription, setDescription, None, "Description's Docstring")

    face = property(getFace, setFace, None, "Face's Docstring")

    xo = property(getXo, setXo, None, "Xo's Docstring")

    yo = property(getYo, setYo, None, "Yo's Docstring")

    xe = property(getXe, setXe, None, "Xe's Docstring")

    ye = property(getYe, setYe, None, "Ye's Docstring")

    width = property(getWidth, setWidth, None, "Width's Docstring")

    height = property(getHeight, setHeight, None, "Height's Docstring")

    action = property(getAction, setAction, None, "Action's Docstring")

    actionArgs = property(getActionArgs, setActionArgs, None, "ActionArgs's Docstring")
    