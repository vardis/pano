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

from pandac.PandaModules import CardMaker
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec3
from pandac.PandaModules import Point3
from pandac.PandaModules import TextureStage

from pano.constants import PanoConstants
from pano.view.VideoPlayer import VideoPlayer


class SpriteRenderInterface:
    """
    Provides an interface for rendering type of operations on sprites.
    Because Sprites are dumb model classes, in the style of structures, the render interface
    provides a way to control various aspects of their rendering.
    You acquire a render interface for a sprite using the currently active NodeRenderer, like this:
        r = game.getView().getNodeRenderer()
        r.getHotspotSprite(hotspot)  
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
            
        # tracks the copies of this sprite when using instancing, contains nodepaths                 
        self.instances = []
        
    def setPos(self, x, y, z):
        self.nodepath.setPos(x, y, z)
        
    def isAnimated(self):
        '''
        @return: True if this sprite is animated and False if otherwise.
        '''
        return self.video is not None or self.sequenceNode is not None
        
        
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
            time = self.sprite.frameRate * frameNum
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
    
    
    def instanceTo(self, x, y, z):
        '''
        Creates a new render instance of the sprite. The instance is linked to the original sprite
        so any changes to the original sprite will affect all its instances.
        '''
        instance = sprite2d.attachNewNode(self.nodepath.getName() + '_instance_' + len(self.instances))
        instance.setPos(x, y, z)
        self.nodepath.instanceTo(instance)
        self.instances.append(instance)
    
    
    def remove(self):
        '''
        Removes the sprite from the rendering process. This call will invalidate the current
        sprite instance as well.
        '''
        for inst in self.instances:
            inst.removeNode()
        self.instances = []
        
        if self.video is not None:            
            self.video.stop()            
        
        self.nodepath.clearTexture()    
        self.nodepath.removeNode() 
        self.nodepath = None


class SpritesEngine:
    """
    Provides utility methods for rendering sprites.
    """        
    
    def __init__(self):
        self.log = logging.getLogger('SpritesUtil')
        
        # the resource loader
        self.resources = None
        
        # a CardMaker instance for building sprite quads
        self.cardMaker = None
        
        # sprites root
        self.sprite2d = None
        
        # root for sprites that need to consider the aspect ratio when rendering
        self.aspect_sprite2d = None
        
        
    def initialize(self, resources):
        '''
        Performs any first-time initializations. 
        '''        
        self.resources = resources
        self.cardMaker = CardMaker('spritesMaker')
        self.cardMaker.setFrame(-0.5, 0.5, -0.5, 0.5)
        self.sprite2d = self._createSpritesNodeSetup(render2d)
        self.aspect_sprite2d = self._createSpritesNodeSetup(aspect2d)
        __builtins__['sprite2d'] = self.sprite2d
        __builtins__['aspect_sprite2d'] = self.aspect_sprite2d
        
        # used to generate unique sprite names
        self.counter = 0            
        
        
    def _createSpritesNodeSetup(self, parent):
        '''
        Setups a new scenegraph that allows using screen coordinates instead of 3D. The conversions are automated
        by the configuration of the scene nodes. 
        '''
        screenWidth = base.win.getXSize()
        screenHeight = base.win.getYSize()
        
        aspect_ratio = parent.getScale()[0]    
    
        screenOrigin = parent.attachNewNode('screen_origin')
        screenNode = screenOrigin.attachNewNode('screen_node')
    
        screenOrigin.setPos(-1.0/aspect_ratio, 0.0, 1.0)
        screenOrigin.setScale(2.0, 1.0, -2.0)
    
        screenNode.setPos(0, 0, 0)
        
        screenNode.setScale(1.0/(aspect_ratio*screenWidth), 1.0, 1.0/screenHeight)
        screenNode.setTexScale(TextureStage.getDefault(), 1.0, -1.0)
        
        # test some points    
    #    points = [(0,0), (screenWidth, 0), (screenWidth, screenHeight), (screenWidth/2.0, screenHeight/2.0), (0, screenHeight)]
    #    for pt in points:
    #        print '%s -> %s' % (pt, str(parent.getRelativePoint(screenNode, Vec3(pt[0], 0, pt[1]))))
        
        return screenNode

    
    def createSprite(self, sprite):
        '''
        Creates a new sprite and returns a SpriteRenderInterface for controlling this sprite instance.
        The newly created sprite is located at (0,0) in screen coordinates its dimensions are specified
        by the given Sprite argument.
        @param sprite: A Sprite resource that describes the properties of the sprite to created.
        @return: A SpriteRenderInterface instance or None if it failed to create the sprite.
        '''
        if sprite.eggFile is not None:
            spriteNP = self.resources.loadModel(sprite.eggFile)
            tex = None
        else:        
            if sprite.video is not None:
                card = self.cardMaker.generate()
                tex = VideoPlayer.renderToTexture(self.resources, video=sprite.video, audio=sprite.audio)
            elif sprite.image is not None:
                card = self.cardMaker.generate()
                tex = self.resources.loadTexture(sprite.image)
            else:
                self.log.error('Could not determine type for sprite: %s' % sprite.name)
                return None
            
            spriteNP = NodePath(card)
            spriteNP.setTexture(tex)
            
        nodeName = self.getSpriteNodeName(sprite.name)             
        spriteNP.setName(nodeName)                    
        spriteNP.setPos(0, 1, 0)
        spriteNP.setScale(sprite.width, 1.0, sprite.height)
        spriteNP.setTransparency(1)
        
        spriteNP.reparentTo(self.sprite2d)
        
        spriteNP.setDepthTest(False)
        spriteNP.setDepthWrite(False)
        spriteNP.setBin("fixed", PanoConstants.RENDER_ORDER_SPRITES)
        spriteNP.setPythonTag('sprite', sprite)
        
        if sprite.video is not None:
            spriteNP.setPythonTag('video', tex)
            tex.setLoop(True)
            tex.play()       
            
        return SpriteRenderInterface(spriteNP)
                 
    
    def getSpriteNodeName(self, spriteName):
        self.counter += 1
        return PanoConstants.SPRITES_NAME_PREFIX + spriteName + ('_%i' % self.counter) 
    
################################ for NodeRenderer ########################################    
class SpritesUtil:
    counter = 0
    
    def createSprite3D(resources, sprite, parentNode):
        nodeName = SpritesUtil.getSpriteNodeName(sprite.name)
        nodePath = None

        if sprite.eggFile is not None:
            nodePath = SpritesUtil.createImageSequenceSprite3D(resources, sprite, parentNode)
        elif sprite.video is not None:
            nodePath = SpritesUtil.createVideoSprite3D(resources, sprite, parentNode)
        elif sprite.image is not None:
            nodePath = SpritesUtil.createImageSprite3D(resources, sprite, parentNode)
        else:
            self.log.error('Could not determine type for sprite: %s' % sprite.name)

        if nodePath is not None:
            nodePath.setName(nodeName)
            nodePath.setDepthTest(False)
            nodePath.setDepthWrite(False)                    
            nodePath.setBin("fixed", PanoConstants.RENDER_ORDER_SPRITES)
            
        return nodePath
    
     
    def createVideoSprite3D(resources, sprite, parent):
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
        video = VideoPlayer.renderToGeom(resources, geom=np, video=sprite.video, audio=sprite.audio)
        np.setPythonTag('video', video)    
        video.setLoop(True)
        video.play()        
        return np


    def createImageSequenceSprite3D(resources, sprite, parent):
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
    
    def createImageSprite3D(resources, sprite, parent = None):
        """
        Creates a node responsible for rendering a sprite whose visual representation consists of a single image.
        
        We use the CardMaker in order to generate a quad where the image will be applied as a texture.        
        
        Returns: the NodePath for the created node.
        """
        tex = resources.loadTexture(sprite.image)
        cm = CardMaker(sprite.name)
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        cm.setColor(1,1,1,1)
        if parent is not None:
            card = parent.attachNewNode(cm.generate())
        else:
            card = NodePath(cm.generate())
        card.setTexture(tex)
        card.setPythonTag('sprite', sprite)
        return card
    
    def getSpriteNodeName(spriteName):
        SpritesUtil.counter += 1
        return PanoConstants.SPRITES_NAME_PREFIX + spriteName + ('_%i' % SpritesUtil.counter) 
    
    createSprite3D              = staticmethod(createSprite3D)
    createVideoSprite3D         = staticmethod(createVideoSprite3D)
    createImageSequenceSprite3D = staticmethod(createImageSequenceSprite3D)
    createImageSprite3D         = staticmethod(createImageSprite3D)
    getSpriteNodeName           = staticmethod(getSpriteNodeName)
    