
class Hotspot:
    """
    Represents the model of a game hotspot. A hotspot is a rectangular area on the
    panoramic view that can interact with the user through the mouse.
    Each hotspot defines the face of the cubemap on which it belongs, the coordinates
    of the top left corner of its rectangular area and the width and height of its area.
    """
    
    def __init__(self, name='', description='', face=None, x=0, y = 0, width = 0, height=0, action=None, params = ()):
        self.name = name
        self.description = description
        self.face = face
        
        # upper left corner coordinates
        self.xo = x
        self.yo = y
        
        # lower right corner coordinates
        self.xe = x + width
        self.ye = y + height
        
        self.width = width
        self.height = height
        self.action = action
        self.actionParams = params
        
    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getFace(self):
        return self.face
    
    def setFace(self, face):
        self.face = face

    def getXo(self):
        return float(self.xo)

    def setXo(self, xo):
        self.xo = xo
        self.xe = xo + self.width

    def getYo(self):
        return float(self.yo)
    
    def setYo(self, yo):
        self.yo = yo
        self.ye = yo + self.height

    def getXe(self):
        return float(self.xe)

    def getYe(self):
        return float(self.ye)

    def getWidth(self):
        return self.width
    
    def setWidth(self, width):
        self.width = width
        self.xe = xo + self.width

    def getHeight(self):
        return self.height
    
    def setHeight(self, height):
        self.height = height
        self.ye = yo + self.height
    
    def getAction(self):
        return self.action
    
    def setAction(self, action):
        self.action = action
    
    def getActionParams(self):
        return self.actionParams
    
    def setActionParams(self, params):
        self.actionParams = params
    