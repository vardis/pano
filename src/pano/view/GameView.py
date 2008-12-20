from pandac.PandaModules import WindowProperties

from NodeRenderer import NodeRenderer
from constants import PanoConstants
from MousePointerDisplay import MousePointerDisplay
from NodeRaycaster import NodeRaycaster
from model.Node import Node

class GameView:    
    def __init__(self, gameRef = None, title = ''):
        self.game = gameRef
        self.window = None
        self.windowProperties = None
        self.title = title
        self.panoRenderer = NodeRenderer(self.game.resources)
        self.raycaster = NodeRaycaster(self.panoRenderer)
        self.raycaster.initialise()
        self.mousePointer = MousePointerDisplay(gameRef)        
        self.activeNode = None                
        
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
            wp.setSize(size[0], size[1])
            
        if props.has_key(PanoConstants.WIN_TITLE):
            wp.setTitle(props[PanoConstants.WIN_TITLE])
                              
        if props.has_key(PanoConstants.WIN_FULLSCREEN):
            wp.setFullscreen(props[PanoConstants.WIN_FULLSCREEN])
            
        if props.has_key(PanoConstants.WIN_MOUSE_POINTER):
            print 'hiding mouse pointer'
            wp.setCursorHidden(not props[PanoConstants.WIN_MOUSE_POINTER])
            
        if props.has_key(PanoConstants.WIN_ICON):
            wp.setIconFilename(props[PanoConstants.WIN_ICON])
            
        self.windowProperties = wp
        base.win.requestProperties(self.windowProperties)
    
    def openWindow(self):        
        if base.openMainWindow(props = self.windowProperties, gsg=base.win.getGsg()):
            self.window = base.win
            self.windowProperties = WindowProperties(self.window.getProperties())
        else:
            self.window = None
    
    def closeWindow(self):
        base.closeWindow(self.window)
                     
        