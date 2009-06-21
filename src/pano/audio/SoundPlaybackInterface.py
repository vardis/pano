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

from pandac.PandaModules import FilterProperties

from pano.model.Sound import Sound


class SoundPlaybackInterface():
    """
    Interface for playback operations on sounds, it provides basic sound control
    """
    
    def __init__(self, pandaSound, positional = False):
        self.log = logging.getLogger('pano.SoundPlaybackInterface')
        self.pandaSound = pandaSound
        self.pandaSound.setFinishedEvent('sound_finished')
        self.prevRate = 1.0
        self.pauseTime = 0.0
        self.paused = False
        self.stopped = False
        self.positional = positional
        self.filters = FilterProperties()

    def play(self, loop=None):
        """
        Plays the sound if it was stopped, plays from beginning if the sound was already playing or resumes a paused sound.
        The parameter loop can be False to indicate no looping, True for endless looping, or a positive integer that indicates
        the loop count.
        """                
        # checks for pause->resume transition
        if self.isPaused():                    
            self.pandaSound.setPlayRate(self.prevRate)
            self.pandaSound.setTime(self.pauseTime)
        else:
            if loop is None:
                if self.pandaSound.getLoop():
                    loop = self.pandaSound.getLoopCount()                    
                    if loop <= 0:
                        loop = True
                else:
                    loop = False
            self.setLoop(loop)  # calls play for us
            
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
            if loop > 0:
                self.pandaSound.setLoop(True)
                if loop > 1:
                    self.pandaSound.setLoopCount(loop)
            else:
                self.pandaSound.setLoop(False)   
        self.pandaSound.play()     
    
    def stop(self):
        """
        Stops the sound.
        """
        self.pandaSound.stop()
        self.stopped = True
    
    def pause(self):
        """
        Pauses the sound.
        """
        self.prevRate = self.pandaSound.getPlayRate()
        self.pauseTime = self.pandaSound.getTime()
        self.pandaSound.stop()        
        self.paused = True         
    
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
        if balance < -1.0:
            balance = -1.0
        elif balance > 1.0:
            balance = 1.0
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

    def isStopped(self):
        '''
        @return: True if the sound has explicitly been stop through a call to stop().
        '''
        return self.stopped
    
    def isPaused(self):
        """
        Returns True if the sound is paused or False if otherwise.
        """
        return self.paused
    
    
    def isFinished(self):
        '''
        @return: True if the sound finished playing.
        '''
        return self.pandaSound.status() == 1 and not self.stopped and not self.paused 

    def configureFilters(self, filters):
        '''
        Configures the DSP filters for this sound.
        @param filters: A list of filter instances.
        '''
        self.filters.clear()
        for f in filters:
            if f.type == Sound.FT_Chorus:
                self.filters.addChorus(f.dryMix, f.wet1, f.wet2, f.wet3, f.delay, f.rate, f.depth, f.feedback)
            elif f.type == Sound.FT_Reverb:
                self.filters.addReverb(f.dryMix, f.wetmix, f.room_size, f.damp, f.width)
            elif f.type == Sound.FT_PitchShift:
                self.filters.addPitchshift(f.pitch, f.fft_size, f.overlap)
            elif f.type == Sound.FT_Flange:
                self.filters.addFlange(f.drymix, f.wetmix, f.depth, f.rate)
            elif f.type == Sound.FT_Compress:
                self.filters.addCompress(f.threshold, f.attack, f.release, f.gain)
            elif f.type == Sound.FT_HighPass:
                self.filters.addHighpass(f.cutoff_freq, f.reasonance_q)
            elif f.type == Sound.FT_LowPass:
                self.filters.addLowpass(f.cutoff_freq, f.reasonance_q)
            elif f.type == Sound.FT_Distort:
                self.filters.addDistort(f.level)
            elif f.type == Sound.FT_Normalize:
                self.filters.addNormalize(f.fade_time, f.threshold, f.max_amp)
            elif f.type == Sound.FT_Parameq:
                self.filters.addParameq(f.center_freq, f.bandwidth, f.gain)
            elif f.type == Sound.FT_Echo:
                self.filters.addEcho(f.drymix, f.wetmix, f.delay, f.decay_ration)
            else:
                self.log.error('Unknown filter type %s' % f.type)

        # apply the filters
        self.pandaSound.configureFilters(self.filters)
                


