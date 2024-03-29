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

from pandac.PandaModules import WindowProperties
from pandac.PandaModules import Texture
from pandac.PandaModules import NodePath
from pandac.PandaModules import VBase3
from direct.showbase.Transitions import Transitions
from direct.interval.IntervalGlobal import *
from direct.filter.FilterManager import FilterManager

from pano.errors.PanoExceptions import GraphicsError
from pano.view.NodeRenderer import NodeRenderer
from pano.view.Node2DRenderer import Node2DRenderer
from pano.constants import PanoConstants
from pano.view.camera import CameraMouseControl
from pano.view.MousePointerDisplay import MousePointerDisplay
from pano.model.Node import Node
from pano.view.TalkBox import TalkBox
from pano.view.inventoryView import InventoryView
from pano.view.sprites import SpritesEngine
from pano.view.VideoPlayer import VideoPlayer
from pano.view.PostProcessManager import PostProcessManager

class GameView:    
    def __init__(self, gameRef = None, title = ''):
        
        self.log = logging.getLogger('pano.view')
                
        self.game = gameRef
        
        # reference to the panda3d window we use for rendering
        self.window = None
        
        # the active window properties
        self.windowProperties = None
        
        # the window title
        self.title = title                                        
        
        # the Node instance that we are displaying         
        self.activeNode = None
        
        # the active transition: fade-in, fade-out or letter-box effect
        self.transition = None                   
        
        # used to linearly interpolate the camera's orientation using a source and a target quaternion
        self.camQuatInterval = None
        
        self.activeVideo = None
        self.videoPlayer = None
        self.videoCallback = None
        
        self.spritesEngine = SpritesEngine()
        
        # performs the rendering of the nodes
        self.panoRenderer = NodeRenderer(self.game.resources, self.spritesEngine)
        
        # for post processing effects
        self.postProcess = PostProcessManager(self.game)

        # renders the mouse pointer and updates its position according to the mouse        
        self.mousePointer = MousePointerDisplay(gameRef)
        
        # rotates the camera according to mouse movement
        self.cameraControl = CameraMouseControl(self.game)
        
        # the view component of the inventory, i.e. renders the inventory model that we pass to it
        self.inventory = InventoryView(gameRef)
        
        self.talkBox = TalkBox(gameRef)
      
        
    def initialize(self):
        '''
        Initialize self and all components on which we are depended.
        '''
        # disables Panda's mouse based camera control
        base.disableMouse()
        
        self.windowProperties = base.win.getProperties()
        base.setFrameRateMeter(self.game.getConfig().getBool(PanoConstants.CVAR_DEBUG_FPS))
        
        self.panoRenderer.initialize()
        self.spritesEngine.initialize(self.game.getResources())
        self.mousePointer.initialize()
        self.postProcess.initialize()
        
        # enable rotation of camera by mouse
        self.cameraControl.setCamera(self.panoRenderer.getCamera())
        self.cameraControl.initialize()        
        self.cameraControl.enable()
        
        self.talkBox.initialize()
        self.inventory.initialize(self.game.getInventory())
        self.transition = Transitions(loader)                                
                
                
    def update(self, millis):
        if millis == 0.0 and self.camQuatInterval is not None:
            self.camQuatInterval.pause()
        elif self.camQuatInterval is not None:
            if  self.camQuatInterval.isStopped(): # and not self.camQuatInterval.isPlaying():
                self.camQuatInterval = None
                self.cameraControl.enable()
            elif not self.camQuatInterval.isPlaying():
                self.camQuatInterval.resume()
                
        if self.activeVideo is not None and self.videoPlayer is not None:
            if self.videoPlayer.hasFinished():
                self.stopVideo()
                
        self.cameraControl.update(millis)
        self.panoRenderer.render(millis)
        self.talkBox.update(millis)
        self.inventory.update(millis)
        self.postProcess.update(millis)

    def getTalkBox(self):
        return self.talkBox


    def getInventoryView(self):
        return self.inventory
        
    def displayNode(self, node):        
        self.activeNode = node
        if type(node) == str:
            self.activeNode = self.game.getResources().loadNode(node)

        if self.activeNode.is3D() and type(self.panoRenderer) != NodeRenderer:
            self.panoRenderer.dispose()
            self.panoRenderer = NodeRenderer(self.game.resources, self.spritesEngine)
            self.panoRenderer.initialize()            
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('Choosed NodeRenderer')

        elif self.activeNode.is2D() and type(self.panoRenderer) != Node2DRenderer:
            self.panoRenderer.dispose()
            self.panoRenderer = Node2DRenderer(self.game.resources, self.spritesEngine)
            self.panoRenderer.initialize()            
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('Choosed Node2DRenderer')            
        
        self.panoRenderer.displayNode(self.activeNode)


    def clearScene(self):
        self.panoRenderer.clearScene()

        
    def raycastNodeAtMouse(self):
        '''
        Performs a raycasting from the current mouse position and returns the hotspot found
        at that location.
        @return: A Hotspot instance if a hotspot was found or None.
        '''
        #This gives up the window coordinates of the mouse in render2d space
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()            
            return self.panoRenderer.raycastHotspots(mpos.getX(), mpos.getY())
        else:
            return None


    def getActiveNode(self):
        return self.activeNode


    def getMousePointer(self):
        """
        Returns a reference to a MousePointer object that controls the mouse pointer.
        """
        return self.mousePointer


    def getCameraController(self):
        return self.cameraControl


    def getWindowProperties(self):
        return self.windowProperties


    def setWindowProperties(self, props = {}):
        wp = WindowProperties()
        if props.has_key(PanoConstants.WIN_ORIGIN):
            origin = props[PanoConstants.WIN_ORIGIN]
            wp.setOrigin(origin[0], origin[1])
            
        if props.has_key(PanoConstants.WIN_SIZE):
            size = props[PanoConstants.WIN_SIZE]
            wp.setSize(size[0], size[1])
            
        if props.has_key(PanoConstants.WIN_TITLE):
            wp.setTitle(props[PanoConstants.WIN_TITLE])
                              
        if props.has_key(PanoConstants.WIN_FULLSCREEN):
            wp.setFullscreen(props[PanoConstants.WIN_FULLSCREEN])
            
        if props.has_key(PanoConstants.WIN_MOUSE_POINTER):
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('hiding mouse pointer')
            wp.setCursorHidden(not props[PanoConstants.WIN_MOUSE_POINTER])
            
        if props.has_key(PanoConstants.WIN_ICON):
            wp.setIconFilename(props[PanoConstants.WIN_ICON])
            
        self.windowProperties = wp
        if self.window is not None:
            base.win.requestProperties(self.windowProperties)


    def openWindow(self):        
        if base.win is not None:
            base.openMainWindow(props = self.windowProperties, gsg=base.win.getGsg())        
        else:
            base.openMainWindow(props = self.windowProperties, type='onscreen')        
        self.window = base.win
        messenger.send("window-event", [self.window])


    def closeWindow(self):
        base.closeWindow(self.window)    


    def getWindow(self):
        return self.window    


    def fadeIn(self, seconds):
        """
        Fades in the camera view in the specified duration in seconds.
        """
        self.transition.fadeIn(seconds)
    
    def fadeOut(self, seconds):
        """
        Fades out the camera view in the specified duration in seconds.
        """
        self.transition.fadeOut(seconds)
        
    def hideLetterBox(self, seconds):
        """
        Hides the black bars from the camera view in the specified duration in seconds.
        """
        self.transition.letterboxOff(seconds)
    
    def showLetterBox(self, seconds):
        """
        Shows the black bars from the camera view in the specified duration in seconds.
        """
        self.transition.letterboxOn(seconds)
        
    def captureMovie(self, name, duration, fps = 30, source = None):
        base.movie(name, duration, fps, 'png', 4, source)
        
    def saveScreenshot(self, filename):
        if base.screenshot(namePrefix = filename, defaultFilename = False) is None:
            raise GraphicsError('Call to base.screenshot failed')
        
        
    def getSpritesFactory(self):
        return self.spritesEngine
        
    def relativeToAbsolute(self, point):
        '''
        Translates the given point from relative coordinates to absolute screen coordinates.
        Returns a tuple of the form (x, y).
        '''
        wp = self.getWindowProperties()
        return (point[0] * wp.getXSize(), point[1] * wp.getYSize())
    
    def absoluteToRelative(self, point):
        '''
        Translates the given point from absolute coordinates to relative screen coordinates.
        Returns a tuple of the form (x, y).
        '''
        wp = self.getWindowProperties()
        return (float(point[0]) / wp.getXSize(), float(point[1]) / wp.getYSize())
            

    def setCameraLookAt(self, lookat, duration = 0.0, blendType = PanoConstants.BLEND_TYPE_ABRUPT):
        '''
        Points the camera to the specified look-at point.
        This point is defined through a string parameter which can take one of the following values:
          a) face_xxxx, where xxxx can be front, back, left, right, top or bottom and denotes the center of the respective face of the cube node.
          b) hotspot_xxx, where xxxx is the name of a hotspot defined within the context of the active node.
        '''
        wp = None
        if lookat.startswith('face_'):
            faceName = lookat[5:]
            face = PanoConstants.CBM_FRONT_FACE
            if faceName == 'front':
                face = PanoConstants.CBM_FRONT_FACE
            elif faceName == 'back':
                face = PanoConstants.CBM_BACK_FACE
            elif faceName == 'right':
                face = PanoConstants.CBM_RIGHT_FACE
            elif faceName == 'left':
                face = PanoConstants.CBM_LEFT_FACE
            elif faceName == 'top':
                face = PanoConstants.CBM_TOP_FACE
            elif faceName == 'bottom':
                face = PanoConstants.CBM_BOTTOM_FACE
            else:
                self.log.error('Wrong lookat attribute: %s for node %s' % (lookat, self.activeNode.getNode()))
                return
            
            wp = self.panoRenderer.getWorldPointFromFacePoint(face, (0.5, 0.5))
            
        elif lookat.startswith('hotspot_'):
            hpName = lookat[8:]
            hp = self.activeNode.getHotspot(hpName)
            wp = self.panoRenderer.getHotspotWorldPos(hp)
                        
        if wp is not None:
            camera = self.panoRenderer.getCamera()
            if duration == 0.0:                            
                camera.lookAt(wp[0], wp[1], wp[2])
            else:                        
                startQuat = camera.getQuat()                
                camera.lookAt(wp[0], wp[1], wp[2])
                targetQuat = camera.getQuat()
                camera.setQuat(startQuat)                
                self.camQuatInterval = LerpQuatInterval(base.cam, duration, targetQuat, None, startQuat, None, blendType=blendType, name='test')
                self.cameraControl.disable()
                self.camQuatInterval.start()
                

    def playVideo(self, videoFile, endCallback):        
        self.stopVideo()
        self.videoPlayer = VideoPlayer('fullscreen_player', self.game.getResources())
        self.videoPlayer.playFullScreen(videoFile)
        self.activeVideo = self.videoPlayer.getAnimInterface()
        if self.activeVideo is None:
            self.log.error('Could not playback video ' + videoFile)
        else:
            self.videoCallback = endCallback
            self.activeVideo.play()
    
    def stopVideo(self):
        if self.videoPlayer is not None:
            self.videoPlayer.stop()
            self.videoPlayer.dispose()
            self.videoPlayer = None
            self.videoCallback()

    def getPostProcess(self):
        return self.postProcess
    

    
    