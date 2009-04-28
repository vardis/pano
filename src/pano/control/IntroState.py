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

from direct.interval.IntervalGlobal import *

from constants import PanoConstants
from control.fsm import FSMState
from control.ExploreState import ExploreState

from view.VideoPlayer import VideoPlayer

class IntroState(FSMState):
    '''
    Controls the state of the game when displaying the introductory videos.
    
    It displays the video sequences defined in the configuration and allows the user to interrupt
    the introduction by pressing a key.
    '''
    
    def __init__(self, gameRef = None, node = None):        
        FSMState.__init__(self, gameRef, PanoConstants.STATE_INTRO)        
        self.log = logging.getLogger('pano.introState')

        self.videoPlayer = None
        
        # list of video files to play, we assume they have an audio as well
        self.videos = []
        
        # index to the active video
        self.activeVid = -1
        
        # delay between videos or images
        self.delay = 0
        
        # set to True when we are transitioning between videos or images
        self.transitioning = False
        
    def enter(self):
        # get a comma separated list of video to play in sequence
        vids = self.getGame().getConfig().get(PanoConstants.CVAR_INTRO_STATE_VIDEOS, '')
        if len(vids) == 0:
            self.videos = []
        else:
            self.videos = vids.split(',')
        
        self.delay = self.getGame().getConfig().getFloat(PanoConstants.CVAR_INTRO_STATE_DELAY, 0.0)
        self.log.debug("video intro delay: %f" % self.delay)                        
        
        self.transitioning = False
                
        self.game.getInput().pushMappings('intro')
    
    def exit(self):
        self.game.getInput().popMappings()
        self.videos = None
        self.activeVid = -1
        self.transitioning = False

    
    def update(self, millis):
        
        if self.videos is None or len(self.videos) == 0:
            self.log.debug('No videos defined, switching to explore state')
            self.getGame().getState().changeState(PanoConstants.STATE_EXPLORE)
            return
        
        # wait for transition to end
        if self.transitioning:
            return
        
        if self.activeVid < 0:
            self.activeVid = 0
            self._playActiveIdVideo()            
        else:                    
            if self.videoPlayer is None or self.videoPlayer.hasFinished():
                # active video ended, check if there are more
                self.activeVid += 1
                if self.activeVid < len(self.videos):
                    if self.delay > 0.0:
                        self.transitioning = True
                        Sequence(Wait(self.delay), Func(self._playActiveIdVideo)).start()
                    else:
                        self._playActiveIdVideo()
                else:
                    # played through all the list, we are done
                    self._stopPlayback()
                    self.log.debug('all videos done') 
                    self.getGame().getState().changeState(PanoConstants.STATE_EXPLORE)
    
    def onInputAction(self, action):
        if action == "interrupt":
            
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('Intro interrupted')
            
            self._stopPlayback()
            self.activeVid = len(self.videos)
            
            return True
        else:
            return False
        
    def _stopPlayback(self):
        if self.videoPlayer is not None:
            self.videoPlayer.stop()
            self.videoPlayer.dispose()
            self.videoPlayer = None
            
    def _playActiveIdVideo(self):
        
        assert self.activeVid < len(self.videos), 'activeId is out of range'
        
        # we are out of transition phase
        self.transitioning = False        
        
        if self.videoPlayer is not None:
            self.videoPlayer.stop()
            self.videoPlayer.dispose()
        
        videoFile = self.videos[self.activeVid]
        self.videoPlayer = VideoPlayer('intro_player', self.getGame().getResources())
        self.videoPlayer.playFullScreen(videoFile, videoFile)
        anim = self.videoPlayer.getAnimInterface()
        if anim is None:
            log.error('Could not playback video ' + videoFile)
        else:
            anim.play()
            