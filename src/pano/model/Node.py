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

    # constants for the parent of 2D nodes
    PT_Aspect2D = 1
    PT_Render2D = 2

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

        # for 3D nodes this specifies the basename (without the extension) of the six textures applied
        # to the cubemap
        self.cubemap = None

        # the image to use as a background for 2D nodes
        self.image = None
        
        # a 4 element list defining the background color for 2D nodes, instead of a background image 
        self.bgColor = None

        # used for overriding the file extension of the cubemap's image (default is .png)
        self.extension = None

        # the hotspots of this node, in { 'name' : <Hotspots instance> } format
        self.hotspots = hotspots if hotspots is not None else {}

        # filename of the script to associate with this node
        self.scriptName = scriptName if scriptName is not None else name

        # specifies the initial camera orientation, see pano.view.GameView.setCameraLookAt for more info.
        self.lookat = lookat

        # the name of the music playlist to activate upon displaying this node
        self.musicPlaylist = None

        # determines which node to use as the scene root, aspect2d or render2d
        self.parent2d = Node.PT_Aspect2D
        
        # filename of the image or quad tree image to be used as a hotspots map in connection
        # with self.hotspotsColorKeys
        self.hotspotsMapFilename = None                    


    def is2D(self):
        return self.cubemap is None and (self.image is not None or self.bgColor is not None)

    def is3D(self):
        return self.cubemap is not None and self.image is None

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
        self.hotspots[hotspot.name] = hotspot
        
    def getHotspot(self, name):
        return self.hotspots.get(name)
        
    def getScriptName(self):
        return self.scriptName
    
    def setScriptName(self, scriptName):
        self.scriptName = scriptName    
        
    def getExtension(self):
        return self.extension
    
    def setExtension(self, extension):
        self.extension = extension
    