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

from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import CollisionHandlerQueue
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import GeomNode

class NodeRaycaster:
    def __init__(self, renderer):
        
        self.log = logging.getLogger('pano.raycaster')
        
        self.renderer = renderer
        
        #Stores the collisions of the camera ray with the cubemap
        self.collisionsQueue = None
        
        #Variables for setting up collision detection in Panda
        self.pickerNP = None
        self.pickerNode = None
        self.pickerRay = None
        self.traverser = None
        
    def initialize(self):
        """
        To setup collision detection we need:
            a. A CollisionNode having a ray as its solid and placed at the position
               of the camera while also having the same orientation as the camera.
            b. A new nodepath placed in the scenegraph as an immediate child of the
               camera. It will be used to insert the collision node in the scenegraph.
            c. A CollisionRay for firing rays based on mouse clicks.
            d. A collisions traverser.
            e. A collisions queue where all found collisions will be stored for later
               processing.
        """
        self.traverser = CollisionTraverser('Hotspots collision traverser')
        self.collisionsQueue = CollisionHandlerQueue()        
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.pickerNP = self.renderer.getCamera().attachNewNode(self.pickerNode)        
        self.traverser.addCollider(self.pickerNP, self.collisionsQueue)
        
    
    def dispose(self):
        if self.pickerNP is not None:
            self.traverser.removeCollider(self.pickerNP)
            self.pickerNode.clearSolids()
            self.pickerNP.removeNode()
            
        
    def raycastWindow(self, x, y, returnAll = False):
        '''
        Casts a camera ray, whose origin is implicitly defined by the given window coordinates, against 
        the rendered scene returns information regarding the hit point, if any.
        
        @param x: The x window coordinate of the ray's origin in render2d space.
        @param y: The y window coordinate of the ray's origin in render2d space 
        @param returnAll: If set to False then only the closest collided geometry is returned, otherwise
        all nodepaths whose collision nodes were intersected by the camera ray will be returned. 
        @return: 
        If returnAll was False, then a list containing a tuple of the form (topmost intersected NodePath, contact point Point3f).
        if returnAll was set to True, a list of tuples in the same form as above, one tuple for each intersection. 
        None if no collision occurred. 
        '''        
        #This makes the ray's origin the camera and makes the ray point 
        #to the screen coordinates of the mouse
        self.pickerRay.setFromLens(self.renderer.getCamera().node(), x, y)
        
        #Check for collision only with the node
        self.traverser.traverse(self.renderer.getSceneRoot())
        
        if self.collisionsQueue.getNumEntries() > 0:
            if not returnAll:
                self.collisionsQueue.sortEntries()
                cEntry = self.collisionsQueue.getEntry(0)
                if cEntry.hasInto():
                    return [(cEntry.getIntoNodePath(), cEntry.getSurfacePoint())]
                else:
                    return None
            else:
                nodepaths = []
                for i in xrange(self.collisionsQueue.getNumEntries()):
                    cEntry = self.collisionsQueue.getEntry(i)
                    if cEntry.hasInto():
#                        self.log.debug('adding collision into-nodepath: %s' % str(cEntry.getIntoNodePath()))
                        intoNP = cEntry.getIntoNodePath()
                        nodepaths.append((intoNP, cEntry.getSurfacePoint(intoNP)))
                return nodepaths
        
        
            