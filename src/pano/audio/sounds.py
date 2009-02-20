import weakref
import logging

from constants import PanoConstants
from SoundPlaybackInterface import SoundPlaybackInterface

class SoundsPlayer():
    """
    Manages playback and the lifetime of sounds.
    Generally you can provide either filenames of .snd files or raw music files
    such as .mp3, .ogg. Use the high level .snd files if you want to provide
    further information such as 3d position, subtitles, etc.
    For efficiency reasons, there is a limit to the number of concurrent active
    sounds and thus it is important to release sound resources when they are 
    no longer needed. But since garbage collection is not deterministic, you
    must call sound.dispose() when you have no more need of the sound object.
    """
    def __init__(self, game):
        self.log = logging.getLogger('pano.soundsPlayer')
        self.game = game
        self.audio3d = None # manager of positional sounds
        self.sounds = []    # list of weak references to sound objects
        self.volume = 1.0   # default volume level
        self.cutOff = None  # default cut-off distance
        self.balance = 0.0  # default balance, -1.0: left, 0.0: center, 1.0: right
        
    def initialize(self):
        pass
#        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)

    def  update(self, millis):
        # remove dead references to sounds
        prevLen = len(self.sounds)
        self.sounds = [snd for snd in self.sounds if snd() is not None]
        rem = prevLen - len(self.sounds)
        if rem > 0:
            self.log.debug('Removed %d dead references!' % rem)
        
    def playSound(self, sndName, loop=None, rate=None):
        """
        Plays the sound that is described by the specified sound resource
        whose properties are defined in the file sndName + '.snd'.
        
        Returns: a Sound object or None if playback failed
        """
        snd = self.game.getResources().loadSound(sndName)
        spath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_SOUNDS, snd.getSoundFile())
        spi = SoundPlaybackInterface(loader.loadSfx(spath))
        loopVal = loop
        if not loopVal:
            loopVal = snd.getLoop()
                        
        if rate is not None:    
            spi.setPlayRate(rate)
        else:
            spi.setPlayRate(snd.getPlayRate())
                        
        spi.play(loopVal)
        spi.setVolume(self.volume)
        spi.setBalance(self.balance)
        self.sounds.append(weakref.ref(spi))
        return spi
        
    
    def playSoundFile(self, filename, loop=False, rate=1.0):
        """
        Plays the specified sound file with the defaul settings.
        
        Returns: a Sound object or None if playback failed
        """
        fp = self.game.getResources().getResourceFullPath(filename)
        sound = loader.loadSfx(fp)
        sound.setLoop(loop)
        sound.setPlayRate(rate)
        sound.play()
        sound.setVolume(self.volume)
        sound.setBalance(self.balance)
        
        spi = SoundPlaybackInterface(sound)
        self.sounds.append(weakref.ref(spi))
        return spi
    
    def stopAll(self):
        """
        Stops all currently playing or paused sounds.
        """
        for spi in self.sounds:
            o = spi()
            if o is not None:
                o.stop()
    
    def pauseAll(self):
        """
        Pauses all currently playing sounds.
        """
        for spi in self.sounds:
            spi.pause()
    
    def resumeAll(self):
        """
        Resumes all currently paused sounds.
        """
        for spi in self.sounds:
            spi.play()
    
    def isSoundPlaying(self, sndName):
        """
        Returns True if the sound described the specified sound resource
        is being playbacked.
        """
        pass
    
    def setVolume(self, volume):
        """
        Sets the global volume level.
        Individual sounds can playback at a different volume level.
        """
        assert 0.0 <= volume and volume <= 1.0, 'valid range for sound volume is 0...1'
        self.volume = volume
    
    def getVolume(self):
        """
        Returns the global volume level.
        """
        return self.volume
    
    def setCutOffDistance(self, dist):
        """
        Sets the default distance beyond which all 3d sounds will be cut off.
        Individual sounds may be set to a different cut-off distance.
        """
        pass
    
    def getCutOffDistance(self):
        """
        Returns the default global cut-off distance.
        """
        pass
    
    def setBalance(self, balance):
        """
        Sets the default global sound balance.
        Individual sounds can be set to a different balance.
        The parameter can take values between -1.0, which denotes full left balance, and
        1.0, which denotes full right balance.
        """
        assert -1.0 <= volume and volume <= 1.0, 'valid range for sound balance is -1...1'
        self.balance = balance
    
    def getBalance(self):
        """
        Returns the default global sound balance.
        """
        return self.balance
    
    
    
    