import math

from direct.task.Task import Task

from constants import PanoConstants
from model.Playlist import Playlist

class MusicPlayer:
    def __init__(self, game):
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
        self.task = taskMgr.add(self.update, "Updates the music")            
         
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
        
        print 'active track ', self.activeTrack
        soundPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_SOUNDS, self.activeTrack[2])
        print 'sound path ', soundPath
        self.sound = loader.loadSfx(soundPath)
        if self.sound is not None:
            self.sound.play()
            self.sound.setVolume(self.volume)
            self.sound.setPlayRate(self.playRate)
            self.stopped = False
            self.paused = False
            
    def getStopped(self):
        return self.stopped


    def setStopped(self, value):
        self.stopped = value
        if self.sound is not None and value:
            self.sound.stop()


    def isPaused(self):
        return self.paused


    def setPaused(self, value):
        self.paused = value        
        if self.sound is not None:
            if value:
                self.sound.setPlayRate(0.0)
            else:
                self.sound.setPlayRate(self.playRate)                
    
    def getActiveTrack(self):
        pass

    def getPlaylist(self):
        return self.playlist

    def getPlayRate(self):
        return self.playRate

    def getVolume(self):
        return self.volume


    def isLooping(self):
        return self.looping


    def setPlaylist(self, value):
        print 'SETTING PLAYLIST'
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

    
    
        