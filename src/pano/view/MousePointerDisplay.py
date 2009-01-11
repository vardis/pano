import logging

from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import CullBinManager
from direct.task.Task import Task

from constants import PanoConstants

class MousePointerDisplay:
    def __init__(self, game):
        
        self.log = logging.getLogger('pano.mouseDisplay')
        
        self.game = game
        self.resources = game.getResources()
        
        self.scale = 0.1
        
        self.pointer = None
        
        #the parent node of the mouse pointer
        self.pointerParentNP = None
        
        #the mouse pointer node, it can be a ModelNode if the cursor is animated and was read by an .egg file
        #or it can be a OnScreenImage if the cursor is static
        self.mousePointer = None
        
        #True if the pointer is a static image and therefore is rendered through a OnScreenImage object
        self.isImagePointer = False
        
        #True if the mouse pointer is hidden
        self.mouseHidden = True                                
        
    def initialize(self):        
        self.pointerParentNP = aspect2d.attachNewNode('mousePointer')
        
        # create a GUI Layer for the pointer
        CullBinManager.getGlobalPtr().addBin('mouse_pointer', CullBinManager.BTUnsorted, 60)
        
        # add task that updates the location of the mouse pointer
        taskMgr.add(self.updatePointerLocationTask, "Mouse Pointer Task")
        
    def isShown(self):
        return not self.mouseHidden
    
    def show(self):        
        if self.pointer is not None:            
            if self.mousePointer is not None:
                if self.isImagePointer:
                    # trigger the actual display of the mouse pointer
                    self.mouseHidden = self.setByName(self.pointerName)
                else:
                    # bring the mouse node back in the scenegraph
                    self.mousePointer.reparentTo(aspect2d)
                    self.mouseHidden = False            
        else:
            self.mouseHidden = True
            
    """
    Hides the mouse pointer.
    For image based pointers, the associated OnScreenImage is destroyed with a call to the member function destroy().
    While for model based pointers the associated model node is simply removed from the scenegraph. 
    """
    def hide(self):
        if not self.mouseHidden:
            base.mouseWatcherNode.setGeometry(None)
            
            self._destroyPointer()
            
            self.mouseHidden = True
            self.pointer = None
            self.mousePointer = None        
            
    def _destroyPointer(self):
        if self.isImagePointer:
            self.mousePointer.destroy()
        else:
            self.mousePointer.removeNode()
    
    def getScale(self):
        return self.scale
    
    def setScale(self, scale):
        self.scale = scale
        
    def setByName(self, pointerName):
        """
        Sets and displays the specified mouse pointer. If None is passed in place
        of the pointerName parameter, then the mouse pointer is hidden.
        
        Convention: A texture file or egg file with a base name equal
        to pointerName must exist in one of the resource locations
        associated with the cursors resource type.
        
        Convention: If the pointer name corresponds to an egg file, then
        the pointer is assumed to be animated. Otherwise the pointer is
        assumed to be a static image.
        
        Returns True if the pointer was set successfully and False if otherwise.
        """        
        pointerChanged = (self.pointer is None) or (pointerName != self.pointer.getName())
        if (pointerName is None) or pointerChanged:
            self.hide()
            
        if pointerChanged:
            self.pointer = self.game.getResources().loadPointer(pointerName)
            if self.pointer is None:
                self.log.error("Could'nt find pointer: %s", pointerName)
                return False
             
            if self.pointer.getEggFile() is not None:
                self.isImagePointer = False
                self.mousePointer = loader.loadModel(fullPath)
                self.mousePointer.reparentTo(self.pointerParentNP)
            else:
                self.isImagePointer = True
                texPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, self.pointer.getTexture())
                self.mousePointer = OnscreenImage(image = texPath, pos = (0.5, 0, 0.5), scale=self.scale, parent=self.pointerParentNP)
                self.mousePointer.setTransparency(TransparencyAttrib.MAlpha)
                
            self.mousePointer.setBin('mouse_pointer', 0)
            self.mousePointer.setDepthTest(False)
            self.mousePointer.setDepthWrite(False)            
            self.mouseHidden = False
            
        return True            
            
    def updatePointerLocationTask(self, task):        
        if self.mousePointer is not None and not self.mouseHidden and self.isImagePointer and base.mouseWatcherNode.hasMouse() and not self.game.isPaused():
            x=base.mouseWatcherNode.getMouseX()
            y=base.mouseWatcherNode.getMouseY()            
            self.mousePointer.setPos(x - 0.05, 0, y)
            
        return Task.cont


    