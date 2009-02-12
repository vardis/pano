
class Sound:
    """
    Defines the properties of a game sound.
    Sound resources are defined in .snd files. 
    """
    
    def __init__(self, name, soundFile = None, volume = 1.0, balance = 0.0, node = None, cutOff = None, rate = 1.0):
        self.name = name            # the logical name of the sound
        self.soundFile = soundFile  # the filename of the actual sound data
        self.volume = volume        # the sound's volume
        self.balance = balance      # the sound's balance
        self.node = node            # the name of the node to attach this sound to
        self.cutOff = cutOff        # the cut off distance
        self.rate = rate            # the play rate
        self.loop = False           # True/False if the sound should loop, or an integer value specifying the loop count
    
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
    def getSoundFile(self):
        return self.soundFile
    
    def setSoundFile(self, soundFile):
        self.soundFile = soundFile
        
    def getVolume(self):
        return self.volume
    
    def setVolume(self, volume):
        self.volume = volume
        
    def getBalance(self):
        return self.balance
    
    def setBalance(self, balance):
        self.balance = balance
        
    def getNode(self):
        return self.node
    
    def setNode(self, node):
        self.node = node
        
    def getCutOffDistance(self):
        return self.cutOff
    
    def setCutOffDistance(self, cutOff):
        self.cutOff = cutOff
        
    def getPlayRate(self):
        return self.rate
    
    def setPlayRate(self, rate):
        self.rate = rate
        
    def getLoop(self):
        return self.loop
        
    def setLoop(self, loop):
        self.loop = loop
            
            
    
    