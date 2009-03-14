

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
        
        
    