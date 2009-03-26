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



class Node:
    """
    Represents the model of a game node, i.e. a static panoramic view of the
    game environment from a specific viewpoint.
    """
    def __init__(self, name = '', desc = '', hotspots = None, scriptName = None, lookat = None):
        """
        Initialises a new instance with the given values for its members
        """
        self.name = name
        self.description = desc
        self.cubemap = None
        self.image = None
        self.hotspots = hotspots if hotspots is not None else {}
        self.scriptName = scriptName if scriptName is not None else name            
        self.lookat = lookat

    def getCubemap(self):
        return self.cubemap


    def getImage(self):
        return self.image


    def setCubemap(self, value):
        self.cubemap = value


    def setImage(self, value):
        self.image = value


    def getName(self):
        return self.name


    def getDescription(self):
        return self.description


    def getHotspots(self):
        return self.hotspots.values()


    def setName(self, value):
        self.name = value


    def setDescription(self, value):
        self.description = value


    def setHotspots(self, value):
        self.hotspots = value

    def addHotspot(self, hotspot):
        self.hotspots[hotspot.getName()] = hotspot
        
    def getHotspot(self, name):
        return self.hotspots.get(name)
        
    def getScriptName(self):
        return self.scriptName
    
    def setScriptName(self, scriptName):
        self.scriptName = scriptName
        
    def getLookAt(self):
        return self.lookat
    
    def setLookAt(self, lookat):
        self.lookat = lookat
        
        
    