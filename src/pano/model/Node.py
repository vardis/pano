

class Node:
    """
    Represents the model of a game node, i.e. a static panoramic view of the
    game environment from a specific viewpoint.
    """
    def __init__(self, name = '', desc = '', hotspots = []):
        """
        Initializes a new instance with the given values for its members
        """
        self.name = name
        self.description = desc
        self.hotspots = hotspots        
        
    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        
    def getDescription(self):
        return self.description

    def setDescription(self, desc):
        self.description = desc
        
    def addHotspot(self, hotspot):
        self.hotspots.append(hotspot)
        
    def getHotspots(self):
        return self.hotspots

    def setHotspots(self, hotspots):
        self.hotspots = hotspots
        
    