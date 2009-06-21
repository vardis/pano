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


import math, logging

from direct.task.Task import Task

from pano.constants import PanoConstants
from pano.model.Playlist import Playlist
from pano.messaging import Messenger

class MusicPlayer:
    def __init__(self, game):
        self.log = logging.getLogger("pano.music")
        self.game = game
        self.playlist = Playlist()
        self.volume = 0.5
        self.looping = False
        self.playRate = 1.0
        self.activeTrack = None
        self.sound = None
        self.task = None  
        self.paused = False
        self.stopped = True      
                
    def initialize(self):
        self.task = taskMgr.add(self.update, PanoConstants.TASK_MUSIC)                
         
    def update(self, task):
        if self.sound is not None:
            if self.sound.status() == 1 and not(self.paused) and not(self.stopped) and (self.sound.getTime() >= self.sound.length()):
                self.stopped = True
                if self.looping:
                    i = self.playlist.nextIndex(self.activeTrack[0])
                    self.activeTrack = self.playlist.getTrack(i)
                    self.playSound(i)
                        
        return Task.cont                    
                     
    def nextTrack(self):
        """
        Plays the next track.
        """        
        i = self.playlist.nextIndex()
        self.playSound(i)
    
    def previousTrack(self):
        """
        Plays the next track.
        """
        i = self.playlist.previousIndex()
        self.playSound(i)
    
    def firstTrack(self):
        """
        Plays the first track.
        """
        i = 0        
        self.playSound(i)
    
    def lastTrack(self):
        """
        Plays the last track.
        """  
        i = self.playlist.count() - 1
        self.playSound(i)       
         
    def play(self):
        self.paused = False
        if self.playlist.count() > 0:            
            i = 0
            if self.activeTrack is not None:
                i = self.activeTrack[0]
            self.playSound(i)
            
    def playSound(self, index):
        """
        Plays the sound located at the specified index within the current playlist.
        """
        # stop current sound
        if self.sound is not None:
            self.sound.stop()
                
        self.log.debug('active track %s ' % repr(self.activeTrack))
        soundPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_MUSIC, self.activeTrack[2])        
        self.log.debug('sound path %s' % soundPath)
        self.sound = loader.loadSfx(soundPath)
        if self.sound is not None:
            self.sound.play()
            self.sound.setVolume(self.volume)
            self.sound.setPlayRate(self.playRate)
            self.stopped = False
            self.paused = False
            
    def isStopped(self):
        return self.stopped


    def stop(self):
        self.stopped = True
        if self.sound is not None:
            self.sound.stop()


    def isPaused(self):
        return self.paused


    def setPaused(self, value):
        self.paused = value        
        if self.sound is not None:
            if value:
                self.log.debug("Music rate set to 0.0")
                t = self.sound.getTime()
                self.sound.stop()
                self.sound.setTime(t)
            else:
                self.log.debug("Music rate set to 1.0")
                self.sound.play()                                
    
    def getActiveTrack(self):
        return self.activeTrack

    def getPlaylist(self):
        return self.playlist

    def getPlayRate(self):
        return self.playRate

    def getVolume(self):
        return self.volume


    def isLooping(self):
        return self.looping


    def setPlaylist(self, value):        
        self.playlist = value
        self.activeTrack = self.playlist.getTrack(0)
        self.looping = self.playlist.loop
        self.volume = self.playlist.volume


    def setVolume(self, value):
        self.volume = math.fabs(value)
        if self.sound is not None:
            self.sound.setVolume(self.volume)

    def setPlayRate(self, value):
        self.playRate = math.fabs(value)
        if self.sound is not None:
            self.sound.setPlayRate(self.playRate)
            
    def setLooping(self, value):
        self.looping = value
        if self.sound is not None:
            self.sound.setLoop(self.looping)        
    