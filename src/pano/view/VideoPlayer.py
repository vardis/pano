
import logging

from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import TextureStage

from constants import PanoConstants
from resources.ResourceLoader import ResourceLoader

class VideoPlayer:
    def __init__(self, name, resources):
        self.log = logging.getLogger('pano.videoPlayer' + name)
        self.resources = resources
        self.texCard = None
        self.texCardNode = None
        self.videoTex = None
        self.vidSound = None
        self.animInterface = None
        
    def dispose(self):
        self._releaseResources()
        
    def playFullScreen(self, video, audio):
        
        self._releaseResources()
        
        self.videoTex = loader.loadTexture(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_VIDEOS, video))
        
        self.texCard = CardMaker("Full screen Video Card for " + video);
        self.texCard.setFrameFullscreenQuad()
        self.texCard.setUvRange(self.videoTex)
        self.texCardNode = NodePath(self.texCard.generate())
        self.texCardNode.reparentTo(render2d)
        self.texCardNode.setTexture(self.videoTex)
        if audio is not None:
            self.vidSound = loader.loadSfx(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_SOUNDS, audio))
            self.videoTex.synchronizeTo(self.vidSound)
            
        self.animInterface = self.videoTex
        if self.vidSound is not None:
            self.animInterface = self.vidSound
            
        self.animInterface.play()
            
    def stop(self):        
        if self.animInterface is not None:            
            self.animInterface.stop()
    
    def pause(self):
        if self.animInterface is not None:
            t = self.animInterface.getTime()
            self.animInterface.stop()
            self.animInterface.setTime(t)
            
    def hasFinished(self):
        if self.animInterface is not None:
             return self.animInterface.getTime() >= self.animInterface.length() 
        else:
            return True
            
    def getAnimInterface(self):
        return self.animInterface        
            
    def _releaseResources(self):        
        if self.texCardNode is not None:
            self.texCardNode.removeNode()
            
        self.texCard = None
        self.texCardNode = None
        self.videoTex = None
        self.vidSound = None
        self.animInterface = None
            
    def renderToTexture(resources, geom, video, audio):
        
        videoTex = loader.loadTexture(resources.getResourceFullPath(PanoConstants.RES_TYPE_VIDEOS, video))
        
        if videoTex is None:
            self.log.error("Couldn't load video " + video)
            return None
        
        if (base.sfxManagerList[0].getType().getName() != "OpenALAudioManager"):
            self.log.error("OpenAL support is not enabled, cannot proceed.")
            return None
    
        if (videoTex.getType().getName() != "MovieTexture"):
            self.log.error("MovieTexture support is not enabled, cannot proceed.")
            return None
        
        geom.setTexture(videoTex)        
        if videoTex.getTexturesPower2():            
            geom.setTexScale(TextureStage.getDefault(), videoTex.getTexScale()) #0.75, 0.5625videoTex.getTexScale())
        
        if audio is not None:
            vidSound = loader.loadSfx(resources.getResourceFullPath(PanoConstants.RES_TYPE_SOUNDS, audio))
            videoTex.synchronizeTo(vidSound)
            return vidSound
        else:
            return videoTex                
        
    renderToTexture = staticmethod(renderToTexture)
            
        