
class SoundPlaybackInterface():
    """
    Interface for playback operations on sounds, it provides basic sound control
    """
    
    def __init__(self, pandaSound):
        self.pandaSound = pandaSound
        self.prevRate = 1.0
        self.pauseTime = 0.0
        self.paused = False
        
    def play(self, loop=False):
        """
        Plays the sound if it was stopped, plays from beginning if the sound was already playing or resumes a paused sound.
        The parameter loop can be False to indicate no looping, True for endless looping, or a positive integer that indicates
        the loop count.
        """
        self.setLoop(loop)
        
        # checks for pause->resume transition
        if self.isPaused():                    
            self.pandaSound.setPlayRate(self.prevRate)
            self.pandaSound.setTime(self.pauseTime)
            
        self.pandaSound.play()
        self.paused = False
    
    def isLooping(self):
        """
        Returns: -1 if there is no looping, 0: for endless looping, N: for looping N times
        """
        if not self.pandaSound.getLoop():
            return -1
        else:
            return self.pandaSound.getLoopCount()
    
    def setLoop(self, loop):        
        if type(loop) == bool:            
            self.pandaSound.setLoop(loop)
        elif type(loop) == int:
            self.pandaSound.setLoop(True)
            self.pandaSound.setLoopCount(loop)        
    
    def stop(self):
        """
        Stops the sound.
        """
        self.pandaSound.stop()
    
    def pause(self):
        """
        Pauses the sound.
        """
        self.prevRate = self.pandaSound.getPlayRate()
        self.pauseTime = self.pandaSound.getTime()
        self.pandaSound.stop()        
        self.paused = True 
    
    def isPaused(self):
        """
        Returns True if the sound is paused or False if otherwise.
        """
        return self.paused
    
    def setVolume(self, volume):
        """
        Sets the sound's volume.
        """        
        self.pandaSound.setVolume(volume)
    
    def getVolume(self):
        """
        Returns the sound's volume.
        """
        return self.pandaSound.getVolume()
    
    def setBalance(self, balance):
        """
        Sets the sound's balance.
        """
        self.pandaSound.setBalance(balance)
    
    def getBalance(self):
        """
        Returns the sound's balance.
        """
        return self.pandaSound.getBalance()
    
    def setPlayRate(self, rate):
        """
        Sets the sound's play rate.
        """
        self.pandaSound.setPlayRate(rate)
    
    def getPlayRate(self):
        """
        Returns the sound's play rate.
        """
        return self.pandaSound.getPlayRate()
    
    def getLength(self):
        """
        Returns the duration of the sound in seconds.
        """
        return self.pandaSound.length()
    
    def getTime(self):
        """
        Returns the time position within the sound.
        """
        return self.pandaSound.getTime()
    
    def setTime(self, t):
        """
        Sets the time position within the sound.
        """
        self.pandaSound.setTime(t)
        
    def isPlaying(self):
        """
        Returns True if the sound is currently playing or False if otherwise.
        """        
        return self.pandaSound.status() == 2
    
    