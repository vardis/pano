
class MousePointer:
    """
    Properties for the mouse pointer. 
    """        

    def __init__(self, name = '', eggFile = None, enableAlpha = False, texture = None, scale = 1.0):
        self.__name = name
        self.__eggFile = eggFile
        self.__texture = texture
        self.__enableAlpha = enableAlpha
        self.scale = scale
    
    def getName(self):
        return self.__name


    def getEggFile(self):
        return self.__eggFile


    def getTexture(self):
        return self.__texture


    def getEnableAlpha(self):
        return self.__enableAlpha


    def setName(self, value):
        self.__name = value


    def setEggFile(self, value):
        self.__eggFile = value


    def setTexture(self, value):
        self.__texture = value


    def getScale(self):
        return self.scale
    
    def setScale(self, scale):
        self.scale = scale

    def setEnableAlpha(self, value):
        self.__enableAlpha = value

    name = property(getName, setName, None, "The name of the mouse pointer, it should be unique")

    eggFile = property(getEggFile, setEggFile, None, "The filename containing the 3D model to display in place of the mouse pointer")

    texture = property(getTexture, setTexture, None, "The filename of the texture to use ass a mouse pointer")

    enableAlpha = property(getEnableAlpha, setEnableAlpha, None, "True if the texture contain alpha information")
    
    