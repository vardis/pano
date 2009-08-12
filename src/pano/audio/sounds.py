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

import logging
import math

from direct.showbase import Audio3DManager
from pandac.PandaModules import NodePath

from pano.constants import PanoConstants
from pano.util import PandaUtil
from pano.model.Sound import Sound 
from pano.audio.SoundPlaybackInterface import SoundPlaybackInterface


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
        self.sounds = []    # list of references to sound objects
        self.unfinishedSounds = [] # list of strong references to sounds still playing
        self.volume = 1.0   # default volume level   
        self.rate = 1.0     # default rate of playback     
        self.balance = 0.0  # default balance, -1.0: left, 0.0: center, 1.0: right
        self.enabled = True # indicates if sounds are enabled in a global scale

        # the following are valid only for positional sounds
        self.dropOffFactor = 1.0    # the rate that sounds attenuate by distance
        self.distanceFactor = 1.0   # the scale of measuring units, the default is a scale of 1.0 to match units with meters
        self.dopplerFactor = 1.0    # the Doppler factor
        
        
    def initialize(self):        
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], self.game.getView().getCamera())


    def  update(self, millis):        
        # drop finished sounds
        prevLen = len(self.sounds)    
        self.sounds = [snd for snd in self.sounds if not snd.isFinished()]
        rem = prevLen - len(self.sounds)
        if rem > 0:
            self.log.debug('Removed %d finished sounds' % rem)

        positionalSounds = [snd for snd in self.sounds if snd.positional != Sound.POS_None]
        for sp in positionalSounds:
            if sp.positional == Sound.POS_Hotspot:
                hp = self.game.getView().activeNode.hotspots.get(sp.node)
                if hp is not None:
                    hpos = self.game.getView().panoRenderer.getHotspotWorldPos(hp)
                    np = NodePath('audio3d_' + sp.name)
                    np.setPos(hpos[0], hpos[1], hpos[2])
                    self.audio3d.attachSoundToObject(sp, np)
                else:
                    self.log.error('Could not find hotspot %s to attach positional sound %s' % (sp.node, sp.name))

            elif snd.positionalType == Sound.POS_Node:
                np = PandaUtil.findSceneNode(sp.node)
                if np is not None:
                    self.audio3d.attachSoundToObject(sp.pandaSound, np)
                else:
                    self.log.error('Could not find node %s to attach positional sound %s' % (snd.pos, snd.name))

        if self.audio3d is not None:
            self.audio3d.setDropOffFactor(self.dropOffFactor)
            self.audio3d.setDistanceFactor(self.distanceFactor)
            self.audio3d.setDopplerFactor(self.dopplerFactor)

        
    def playSound(self, sndName, loop=None, rate=None):
        """
        Plays the sound that is described by the specified sound resource
        whose properties are defined in the file sndName + '.snd'.
        
        Returns: a Sound object or None if playback failed
        """
        if self.enabled:
            snd = self.game.getResources().loadSound(sndName)        
                    
            loopVal = loop if loop is not None else snd.loop
            rateVal = rate if rate is not None else snd.playRate
            if rateVal is None:
                rateVal = self.rate
    
            is3D = snd.positional != Sound.POS_None
            spi = self.playSoundFile(snd.soundFile, loopVal, rateVal, is3D)
            spi.configureFilters(snd.getActiveFilters())
    
            # 3d sounds with an absolute position can be specified here just once
            # for other positional types we specify them in the update method
            if is3D and snd.positional == Sound.POS_Absolute:
                np = NodePath('audio3d_' + snd.name)
                np.setPos(snd.node[0], snd.node[1], snd.node[2])
                self.audio3d.attachSoundToObject(snd, np)
    
            return spi

    
    def playSoundFile(self, filename, loop=False, rate=1.0, is3D = False):
        """
        Plays the specified sound file with the defaul settings.
        
        Returns: a Sound object or None if playback failed
        """
        if self.enabled:
            fp = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_SFX, filename)
            try:
                if is3D:
                    sound = self.audio3d.loadSfx(fp)
                else:
                    sound = loader.loadSfx(fp)
            except Exception:
                self.log.exception('An error occured while attempting to load sound %s' % filename)
                return None
                
            spi = SoundPlaybackInterface(sound, is3D)
            spi.setLoop(loop)
            spi.setPlayRate(rate)
            spi.setVolume(self.volume)
            spi.setBalance(self.balance)
            spi.play()                
            
            self.sounds.append(spi)
            return spi
    
    def stopAll(self):
        """
        Stops all currently playing or paused sounds.
        """
        for spi in self.sounds:            
            spi.stop()
    
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
        is being played.
        """
        pass
    
    def setVolume(self, volume):
        """
        Sets the global volume level.
        Individual sounds can playback at a different volume level.
        """
        if volume < 0.0:
            volume = 0.0
        elif volume > 1.0:
            volume = 1.0
            
        self.volume = volume
    
    def getVolume(self):
        """
        Returns the global volume level.
        """
        return self.volume    
    
    
    def getPlayRate(self):
        '''
        Returns the currently default rate of playback.
        '''
        return self.rate
    
    def setPlayRate(self, value):
        '''
        Sets the currently default rate of playback.
        '''        
        self.rate = value


    def getBalance(self):
        '''
        Returns the currently default sound balance.
        '''
        return self.balance

    
    def setBalance(self, value):
        '''
        Changes the balance of a sound. The range is between -1.0 to 1.0. Hard left is -1.0 and hard right is 1.0. 
        '''
        if value < -1.0:
            value = -1.0
        elif value > 1.0:
            value = 1.0
        self.balance = value

    def enableSounds(self):
        '''
        Enables playback of sounds. Sounds are enabled by default.
        '''
        self.enabled = True
        base.enableSoundEffects(True)

    def disableSounds(self):
        '''
        Disables sounds playback. 
        '''
        self.enabled = False
        base.enableSoundEffects(False)

    def isEnabled(self):
        '''
        @return: True if sounds are enabled and False if otherwise.
        '''
        return self.enabled

    
    