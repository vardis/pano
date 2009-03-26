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
from direct.showbase.Transitions import Transitions

from pano.exceptions.PanoExceptions import GraphicsError
from NodeRenderer import NodeRenderer
from constants import PanoConstants
from MousePointerDisplay import MousePointerDisplay
from NodeRaycaster import NodeRaycaster
from model.Node import Node
from TalkBox import TalkBox
from inventoryView import InventoryView

class GameView:    
    def __init__(self, gameRef = None, title = ''):
        
        self.log = logging.getLogger('pano.view')
        self.game = gameRef
        self.window = None
        self.windowProperties = None
        self.title = title
        self.panoRenderer = NodeRenderer(self.game.resources)
        self.raycaster = NodeRaycaster(self.panoRenderer)        
        self.mousePointer = MousePointerDisplay(gameRef)
        self.inventory = InventoryView(gameRef)
        self.__talkBox = TalkBox(gameRef)         
        self.activeNode = None
        self.transition = None   
        
    def initialize(self):
        self.windowProperties = base.win.getProperties()
        base.setFrameRateMeter(self.game.getConfig().getBool(PanoConstants.CVAR_DEBUG_FPS))
        self.panoRenderer.initialize()
        self.mousePointer.initialize()
        self.raycaster.initialize()
        self.__talkBox.initialize()
        self.inventory.initialize(self.game.getInventory())
        self.transition = Transitions(loader)        
                     

    def getTalkBox(self):
        return self.__talkBox

    def setTalkBox(self, value):
        self.__talkBox = value

    def getInventoryView(self):
        return self.inventory
        
    def displayNode(self, node):
        self.activeNode = node
        self.panoRenderer.displayNode(self.activeNode)
        
    def raycastNodeAtMouse(self):
        #This gives up the screen coordinates of the mouse
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            return self.raycaster.raycastMouse(mpos.getX(), mpos.getY())
        else:
            return None
        
    def getActiveNode(self):
        return self.activeNode
            
    """
    Returns a reference to a MousePointer object that controls the mouse pointer.
    """
    def getMousePointer(self):
        return self.mousePointer
    
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
    
    def closeWindow(self):
        base.closeWindow(self.window)
                     
        
    def update(self, millis):
        self.panoRenderer.render(millis)
        self.talkBox.update(millis)
        self.inventory.update(millis)
        
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
        
    def convertScreenToAspectCoords(self, pointsList):
        wp = self.getWindowProperties()
        # the two factors below will convert x and y components into the [0.0...2*base.a2dRight] and [0...2*base.a2dTop] 
        # ranges respectively
        aspectXScale = (1.0 / wp.getXSize()) * (base.a2dRight - base.a2dLeft)
        aspectYScale = (1.0 / wp.getYSize()) * (base.a2dTop - base.a2dBottom)
        retList = []
        for p in pointsList: 
            # subtract maximum values to scale into [base.a2dLeft...base.a2dRight] and [base.a2dBottom...base.a2dTop]
            # and reverse y direction too            
            x = p[0]*aspectXScale - base.a2dRight
            y = -1.0*(p[1]*aspectYScale - base.a2dTop)
            retList.append((x, y))
        return retList
    
    def convertAspectToScreenCoords(self, pointsList):
        """
        Converts a list of points defined in the aspect2d coordinate space, to the screen coordinate space.
        Returns a list of transformed points.
        """
        retList = []
        for p in pointsList:
            # this converts into the [-1.0...1.0] range
            rp = render2d.getRelativePoint(aspect2d, Point3(p[0], 0, p[1]))
            # scale to viewport and add, y also needs reversing
            x = ((rp[0] + 1.0) / 2.0) * wp.getXSize()
            y = -1.0*((rp[0] + 1.0) / 2.0) * wp.getYSize()
            retList.append((x, y))
        return retList

    talkBox = property(getTalkBox, setTalkBox, None, "TalkBox's Docstring")
        
    
    