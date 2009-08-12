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

from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import CullBinManager
from pandac.PandaModules import Point3
from direct.task.Task import Task

from pano.constants import PanoConstants

class MousePointerDisplay:
    def __init__(self, game):
        
        self.log = logging.getLogger('pano.mouseDisplay')
        
        self.game = game
        self.resources = game.getResources()
        
        self.defaultScale = 0.05
        
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
        
        # the name of the image used as a pointer through a call to setImageAsPointer
        self.pointerImage = None                               
        
    def initialize(self):        
        self.pointerParentNP = render2d.attachNewNode('mousePointer')
        
        # create a GUI Layer for the pointer
        CullBinManager.getGlobalPtr().addBin(PanoConstants.MOUSE_CULL_BIN_NAME, CullBinManager.BTUnsorted, PanoConstants.MOUSE_CULL_BIN_VAL)
        
        # add task that updates the location of the mouse pointer
        taskMgr.add(self.updatePointerLocationTask, PanoConstants.TASK_MOUSE_POINTER)
        
    def isShown(self):
        return not self.mouseHidden
    
    def show(self):
        self.mouseHidden = False
        self.pointerParentNP.show()
 
                
    def hide(self):
        """
        Hides the mouse pointer.
        For image based pointers, the associated OnScreenImage is destroyed with a call to the member function destroy().
        While for model based pointers the associated model node is simply removed from the scenegraph. 
        """        
        self.mouseHidden = True
        self.pointerParentNP.hide()
            
    def _destroyPointer(self):        
        if self.mousePointer is not None:
            if self.isImagePointer:
                self.mousePointer.destroy()
                self.mousePointer = None                
            else:
                self.mousePointer.removeNode()
#                self.mousePointer.detachNode() 
            
            if self.pointerParentNP is not None:
                self.pointerParentNP.node().removeAllChildren()
                
            self.isImagePointer = False
            self.pointerImage = None
            self.mousePointer = None
            self.pointer = None
            self.mouseHidden = True
    
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
            self._destroyPointer()
            
        if pointerChanged:
            self.pointer = self.game.getResources().loadPointer(pointerName)
            if self.pointer is None:
                self.log.error("Could'nt find pointer: %s", pointerName)
                return False
             
            if self.pointer.getModelFile() is not None:                
                self.isImagePointer = False
                self.mousePointer = self.game.getResources().loadModel(self.pointer.getModelFile())
                self.mousePointer.setScale(self.pointer.getScale() if self.pointer.getScale() is not None else self.defaultScale)
                self.mousePointer.setTag('model', 'True')
                self.mousePointer.reparentTo(self.pointerParentNP)
                self.isImagePointer = False
                self.pointerImage = None
            else:                
                self.setImageAsPointer(self.pointer.getTexture(), self.pointer.getScale())
                
            self.mousePointer.setTransparency(TransparencyAttrib.MAlpha)            
            self.mousePointer.setBin("fixed", PanoConstants.RENDER_ORDER_MOUSE_POINTER)
            self.mousePointer.setDepthTest(False)
            self.mousePointer.setDepthWrite(False)            
            self.mouseHidden = False
            self.show()
            
        return True   
    
    def setImageAsPointer(self, image, scale = None):
        self._destroyPointer()
        self.isImagePointer = True        
        texPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, image)
        if texPath is not None:
            x, y = 0, 0
            if base.mouseWatcherNode.hasMouse():
                x=base.mouseWatcherNode.getMouseX()
                y=base.mouseWatcherNode.getMouseY()
                                                         
            self.mousePointer = OnscreenImage(
                                              parent=self.pointerParentNP, 
                                              image = texPath, 
                                              pos = Point3(x, 0, y), 
                                              scale = scale if scale is not None else self.defaultScale 
                                              )
            
            self.pointerImage = image
            self.mousePointer.setTransparency(TransparencyAttrib.MAlpha)            
            self.mousePointer.setBin("fixed", PanoConstants.RENDER_ORDER_MOUSE_POINTER)
            self.mousePointer.setDepthTest(False)
            self.mousePointer.setDepthWrite(False)            
            self.mouseHidden = False
            self.show()
            return True
        else:
            return False

    def getPosition(self):
        '''
        Returns the current location of the mouse pointer.
        @return: A (x, y) tuple containing the coordinates of the pointers in the coordinate of the render node.
        '''
        if self.mousePointer is not None:
            pos = self.mousePointer.getPos(render)            
            return (pos[0], pos[2])
        else:
            return (-1, 1)
            
    def updatePointerLocationTask(self, task):   
        if base.mouseWatcherNode.hasMouse():     
            if self.mousePointer is not None and not self.mouseHidden  and base.mouseWatcherNode.hasMouse() and not self.game.isPaused():
                x=base.mouseWatcherNode.getMouseX()
                y=base.mouseWatcherNode.getMouseY()            
                self.mousePointer.setPos(Point3(x, 0, y))
            
        return Task.cont

    def persistState(self, persistence):
        ctx = persistence.createContext('mouse_pointer')
        ctx.addVar('is_image', self.isImagePointer)
        ctx.addVar('scale', self.scale)
        ctx.addVar('pointer_name', self.pointer.getName() if self.pointer is not None else '')
        ctx.addVar('image', self.pointerImage if self.pointer is None else '')
        return ctx
    
    def resumeState(self, persistence):
        pass
    