
import logging

from direct.interval.IntervalGlobal import *

from constants import PanoConstants
from control.fsm import FSMState
from control.ExploreState import ExploreState

from view.VideoPlayer import VideoPlayer

class IntroState(FSMState):
    
    NAME = 'IntroState'
    
    def __init__(self, gameRef = None, node = None):        
        FSMState.__init__(self, gameRef, self.NAME)        
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
                
    
    def exit(self):
        self.videos = None
        self.activeVid = -1
        self.transitioning = False

    
    def update(self, millis):
        
        if self.videos is None or len(self.videos) == 0:
            self.log.debug('No videos defined, switching to explore state')
            self.getGame().getState().changeState(ExploreState.NAME)
            return
        
        # wait for transition to end
        if self.transitioning:
            return
        
        if self.activeVid < 0:
            self.activeVid = 0
            self._playActiveIdVideo()            
        else:                    
            if self.videoPlayer.hasFinished():
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
                    if self.videoPlayer is not None:
                        self.videoPlayer.stop()
                        self.videoPlayer.dispose()
                    self.log.debug('all videos done')
                    self.getGame().getState().changeState(ExploreState.NAME)
            
            
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
            