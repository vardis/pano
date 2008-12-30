

class Node:
    """
    Represents the model of a game node, i.e. a static panoramic view of the
    game environment from a specific viewpoint.
    """
    def __init__(self, name = '', desc = '', hotspots = []):
        """
        Initializes a new instance with the given values for its members
        """
        self.__name = name
        self.__description = desc
        self.__cubemap = None
        self.__image = None
        self.__hotspots = hotspots            

    def getCubemap(self):
        return self.__cubemap


    def getImage(self):
        return self.__image


    def setCubemap(self, value):
        self.__cubemap = value


    def setImage(self, value):
        self.__image = value


    def getName(self):
        return self.__name


    def getDescription(self):
        return self.__description


    def getHotspots(self):
        return self.__hotspots


    def setName(self, value):
        self.__name = value


    def setDescription(self, value):
        self.__description = value


    def setHotspots(self, value):
        self.__hotspots = value


    def addHotspot(self, hotspot):
        self.__hotspots.append(hotspot)
        

    name = property(getName, setName, None, "Name's Docstring")

    description = property(getDescription, setDescription, None, "Description's Docstring")

    hotspots = property(getHotspots, setHotspots, None, "Hotspots's Docstring")

    cubemap = property(getCubemap, setCubemap, None, "Cubemap's Docstring")

    image = property(getImage, setImage, None, "Image's Docstring")
        
        
        
    