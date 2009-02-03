
from constants import PanoConstants
from view.VideoPlayer import VideoPlayer

class SpriteRenderInterface:
    """
    Provides an interface for rendering type of operations on sprites.
    Because Sprites are dumb model classes, in the style of structures, the render interface
    provides a way to control various aspects of their rendering.
    You acquire a render interface for a sprite using the currently active NodeRenderer, like this:
        r = game.getView().getNodeRenderer()
        r.getSpriteRenderInterface(hotspot.getSprite()) or r.getSpriteRenderInterface(sprite.getName()) 
    """
    
    # constants for status
    PLAYING = 1
    STOPPED = 2
    PAUSED  = 3
    
    def __init__(self, nodepath):
        self.nodepath = nodepath
        self.sprite = nodepath.getPythonTag('sprite')
        self.video = nodepath.getPythonTag('video')
        self.status = self.STOPPED 
        self.sequenceNode = self.nodepath.find('**/+SequenceNode')
        if self.sequenceNode is not None and not self.sequenceNode.isEmpty():
            self.sequenceNode = self.sequenceNode.node()
        else:
            self.sequenceNode = None            
        
        
    def play(self):
        """
        Plays the sprite animation starting from the current frame if it was already paused
        or from frame 0 if it was stopped.
        It has no effect if the sprite is already playing.
        """        
        if self.video is not None:
            self.video.play()
        else:            
            self.sequenceNode.play()
            
        self.status = self.PLAYING
        
    
    def stop(self):
        if self.video is not None:      
            self.video.stop()
        else:
            self.sequenceNode.stop()   
                     
        self.status = self.STOPPED
    
    def pause(self):
        if self.video is not None:      
            t = self.video.getTime()
            self.video.stop()
            self.video.setTime(t)
        else:
            self.sequenceNode.stop()   
        
        self.status = self.PAUSED
    
    def isPaused(self):
        return self.status == self.PAUSED
    
    def setFrame(self, frameNum):
        if self.video is not None:      
            # calculate time for the requested frame            
            time = self.sprite.getFrameRate() * frameNum
            self.video.setTime(float(time))            
            self.video.play()
        else:
            play = self.sequenceNode.isPlaying()
            self.sequenceNode.pose(frameNum)
            
            # seq.pose will pause the animation, so check if we must call play
            if play:
                self.sequenceNode.loop(False)        
    
    def hide(self):
        self.nodepath.hide()        
    
    def show(self):
        self.nodepath.show()        
    
    def isVisible(self):
        return not self.nodepath.isHidden()        


class SpritesUtil:
    """
    Provides utility methods for rendering sprites.
    """
    def createVideoSprite(resources, sprite, parent):
        """
        Creates a node responsible for rendering a video sprite.
        
        For video sprites we use a finite plane on which the video will be displayed as a movie texture.
        The VideoPlayer class is used to initiate video & audio playback and to acquire an animation interface 
        which is stored as an attribute at the nodepath level. 
        
        Returns: the NodePath for the created node.
        """
        # loads a plane that extends from -0.5 to 0.5 in XZ plane, face towards world -Y
        np = loader.loadModel(resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, 'plane.egg'))
        np.reparentTo(parent)
        np.setPythonTag('sprite', sprite)
        video = VideoPlayer.renderToTexture(resources, geom=np, video=sprite.getVideo(), audio=sprite.getAudio())
        np.setPythonTag('video', video)    
        video.setLoop(True)
        video.play()        
        return np


    def createImageSequenceSprite(resources, sprite, parent):
        """
        Creates a node responsible for rendering an image sequence animated sprite.
        
        For sprites animated through a sequence of images we assume that the user has already constructed
        an appropriate model file through the egg-texture-cards utility. 
        With this assumption, we only need to load the model and insert it in the scenegraph for rendering.
        
        Returns: the NodePath for the created node.
        """
        eggPath = resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, sprite.eggFile)
        textureCard = loader.loadModel(eggPath)        
        textureCard.reparentTo(parent)
        textureCard.setPythonTag('sprite', sprite)                
        return textureCard
    
    def getSpriteNodeName(spriteName):
        return PanoConstants.SPRITES_NAME_PREFIX + spriteName
    
    createVideoSprite         = staticmethod(createVideoSprite)
    createImageSequenceSprite = staticmethod(createImageSequenceSprite)
    getSpriteNodeName         = staticmethod(getSpriteNodeName)
    