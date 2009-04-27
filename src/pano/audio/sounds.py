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
                
        loopVal = loop if loop is not None else snd.getLoop()
        rateVal = rate if rate is not None else snd.getPlayRate()        
        
        return self.playSoundFile(snd.getSoundFile(), loopVal, rateVal)                    
    
    def playSoundFile(self, filename, loop=False, rate=1.0):
        """
        Plays the specified sound file with the defaul settings.
        
        Returns: a Sound object or None if playback failed
        """
        fp = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_SFX, filename)
        sound = loader.loadSfx(fp)
        spi = SoundPlaybackInterface(sound)
        spi.setLoop(loop)
        spi.setPlayRate(rate)
        spi.setVolume(self.volume)
        spi.setBalance(self.balance)
        spi.play()                
        
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
    
    