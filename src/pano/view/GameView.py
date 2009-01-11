import logging

from pandac.PandaModules import WindowProperties
from NodeRenderer import NodeRenderer
from constants import PanoConstants
from MousePointerDisplay import MousePointerDisplay
from NodeRaycaster import NodeRaycaster
from model.Node import Node
from TalkBox import TalkBox

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
        self.__talkBox = TalkBox(gameRef)         
        self.activeNode = None   
        
    def initialize(self):
        base.setFrameRateMeter(self.game.getConfig().getBool(PanoConstants.CVAR_DEBUG_FPS))
        self.panoRenderer.initialize()
        self.mousePointer.initialize()
        self.raycaster.initialize()
        self.__talkBox.initialize()
                     

    def getTalkBox(self):
        return self.__talkBox

    def setTalkBox(self, value):
        self.__talkBox = value

        
    def displayNode(self, node):
        self.activeNode = node
        self.panoRenderer.displayNode(self.activeNode)
        
    def raycastNodeAtMouse(self):
        #This gives up the screen coordinates of the mouse
        mpos = base.mouseWatcherNode.getMouse()
        return self.raycaster.raycastMouse(mpos.getX(), mpos.getY())
        
    def getActiveNode(self):
        return self.activeNode
            
    """
    Returns a reference to a MousePointer object that controls the mouse pointer.
    """
    def mousePointer(self):
        return self.mousePointer
    
    def setWindowProperties(self, props = {}):
        wp = WindowProperties()
        if props.has_key(PanoConstants.WIN_ORIGIN):
            origin = props[PanoConstants.WIN_ORIGIN]
            wp.setOrigin(origin[0], origin[1])
            
        if props.has_key(PanoConstants.WIN_SIZE):
            size = props[PanoConstants.WIN_SIZE]
            print size
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

    talkBox = property(getTalkBox, setTalkBox, None, "TalkBox's Docstring")
        
    