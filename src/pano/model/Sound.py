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


class Sound:
    """
    Defines the properties of a game sound.
    Sound resources are defined in .snd files. 
    """
    
    def __init__(self, name, soundFile = None, volume = 1.0, balance = 0.0, node = None, cutOff = None, rate = 1.0, subtitles = None):
        self.name = name            # the logical name of the sound
        self.soundFile = soundFile  # the filename of the actual sound data
        self.volume = volume        # the sound's volume
        self.balance = balance      # the sound's balance
        self.node = node            # the name of the node to attach this sound to
        self.cutOff = cutOff        # the cut off distance
        self.rate = rate            # the play rate
        self.loop = False           # True/False if the sound should loop, or an integer value specifying the loop count
        self.subtitles = subtitles  # the key of the message to display as subtitles to this sound
    
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
            
    def getSubtitles(self):
        return self.subtitles
    
    def setSubtitles(self, subs):
        self.subtitles = subs
            
    
    