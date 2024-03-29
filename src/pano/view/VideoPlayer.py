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

from pandac.PandaModules import MovieTexture
from pandac.PandaModules import AudioSound
from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import Texture
from pandac.PandaModules import TextureStage

from pano.constants import PanoConstants
from pano.resources.ResourceLoader import ResourceLoader

class VideoPlayer:
    def __init__(self, name, resources):
        self.log = logging.getLogger('pano.videoPlayer' + name)
        self.resources = resources
        self.texCard = None
        self.texCardNode = None
        self.videoTex = None
        self.vidSound = None
        self.animInterface = None
        
        # has the length of a movie in seconds
        self.totalTime = 0.0
        
    def dispose(self):
        self._releaseResources()
        
    def playFullScreen(self, video, audio = None):
        
        self._releaseResources()
        
#        self.videoTex = loader.loadTexture(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_VIDEOS, video))
        self.videoTex = MovieTexture('name')
        self.videoTex.read(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_VIDEOS, video))
        
        self.texCard = CardMaker("Full screen Video Card for " + video);
        self.texCard.setFrameFullscreenQuad()
        self.texCard.setUvRange(self.videoTex)
        self.texCardNode = NodePath(self.texCard.generate())
        self.texCardNode.reparentTo(render2d)
        self.texCardNode.setTexture(self.videoTex)
        if audio is not None:
            self.vidSound = loader.loadSfx(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_MUSIC, audio))
            self.videoTex.synchronizeTo(self.vidSound)
            
        self.animInterface = self.videoTex
        if self.vidSound is not None:
            self.animInterface = self.vidSound
            
        self.totalTime = self.videoTex.getTime()
        self.animInterface.setLoop(False)
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
            if type(self.animInterface) == AudioSound:
                return self.animInterface.getTime() >= self.animInterface.length()
            else:                
                return self.totalTime <= self.animInterface.getTime()
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
        self.totalTime = 0.0
            
    def renderToGeom(resources, geom, video, audio):
        
        videoTex = loader.loadTexture(resources.getResourceFullPath(PanoConstants.RES_TYPE_VIDEOS, video))
        
        if videoTex is None:
            print "Couldn't load video %s" % video
            return None
        
#        if (base.sfxManagerList[0].getType().getName() != "OpenALAudioManager"):
#            self.log.error("OpenAL support is not enabled, cannot proceed.")
#            return None
    
        if (videoTex.getType().getName() != "MovieTexture"):
            print "MovieTexture support is not enabled, cannot proceed."
            return None
        
        geom.setTexture(videoTex)      
        videoTex.setWrapU(Texture.WMClamp)
        videoTex.setWrapV(Texture.WMClamp)  
        if videoTex.getTexturesPower2():            
            geom.setTexScale(TextureStage.getDefault(), videoTex.getTexScale()) 
        
        if audio is not None:
            vidSound = loader.loadSfx(resources.getResourceFullPath(PanoConstants.RES_TYPE_MUSIC, audio))
            videoTex.synchronizeTo(vidSound)
            return vidSound
        else:
            return videoTex                
        
        
    def renderToTexture(resources, video, audio):
        
        videoTex = loader.loadTexture(resources.getResourceFullPath(PanoConstants.RES_TYPE_VIDEOS, video))
        
        if videoTex is None:
            print "Couldn't load video %s" % video
            return None        
    
        if (videoTex.getType().getName() != "MovieTexture"):
            print "MovieTexture support is not enabled, cannot proceed."
            return None
                
        videoTex.setWrapU(Texture.WMClamp)
        videoTex.setWrapV(Texture.WMClamp)  
        #TODO: Check how I can set the texture scale
#        if videoTex.getTexturesPower2():            
#            geom.setTexScale(TextureStage.getDefault(), videoTex.getTexScale()) 
        
        if audio is not None:
            vidSound = loader.loadSfx(resources.getResourceFullPath(PanoConstants.RES_TYPE_MUSIC, audio))
            videoTex.synchronizeTo(vidSound)
            return vidSound
        else:
            return videoTex
        
    renderToGeom = staticmethod(renderToGeom)
    renderToTexture = staticmethod(renderToTexture)
            
        