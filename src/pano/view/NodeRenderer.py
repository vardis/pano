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
from pano.view.sprites import SpriteRenderInterface

import os
import math
import logging

from pandac.PandaModules import Texture, NodePath
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionPolygon
from pandac.PandaModules import TextureAttrib, CullFaceAttrib
from pandac.PandaModules import GeomVertexReader
from pandac.PandaModules import LineSegs
from pandac.PandaModules import Filename
from pandac.PandaModules import PerspectiveLens
from direct.showbase.PythonUtil import *
from pandac.PandaModules import Mat4, VBase3

from pano.constants import PanoConstants
from pano.view.VideoPlayer import VideoPlayer
from pano.view.NodeRaycaster import NodeRaycaster
from pano.view.sprites import *

# Check these two posts:
# http://www.panda3d.net/phpbb2/viewtopic.php?t=2022&highlight=projection
# http://www.panda3d.net/phpbb2/viewtopic.php?t=851&highlight=skybox
class NodeRenderer:
    """
    Manages the rendering of currently active game node.
    
    To display a game node you need to call NodeRenderer.displayNode(node) and supply to it
    the Node model object.
    """
    
    FRUSTUM_NEAR   = 0
    FRUSTUM_FAR    = 1
    FRUSTUM_RIGHT  = 2
    FRUSTUM_LEFT   = 3
    FRUSTUM_TOP    = 4
    FRUSTUM_BOTTOM = 5

    EPSILON_POS = 0.0001

    def __init__(self, resources, spriteEngine):           

        self.log = logging.getLogger('pano.cubemapRenderer')        
        
        self.resources = resources
        
        # the Node that is being rendered 
        self.node = None
        
        # the dimension of the cubemap
        self.faceDim = 0
        self.faceHalfDim = 0        
        
        # the node that hosts the cubemap model
        self.cmap = None
                
        # the names of the geoms that correspond to the cube's faces
        self.cubeGeomsNames = {
                     PanoConstants.CBM_TOP_FACE    : 'top',
                     PanoConstants.CBM_LEFT_FACE   : 'left',
                     PanoConstants.CBM_BOTTOM_FACE : 'bottom',
                     PanoConstants.CBM_RIGHT_FACE  : 'right',
                     PanoConstants.CBM_BACK_FACE   : 'back',
                     PanoConstants.CBM_FRONT_FACE  : 'front'                     
        }
        
        # matrices that transform from world space to the faces' image space
        self.worldToFaceMatrices = {}
        
        # matrices that transform from the faces' image space to world space  
        self.faceToWorldMatrices = {}
        
        #Stores the textures of the faces. E.g.:
        #frontTexture = self.faceTextures[CBM_FRONT_FACE]        
        self.facesGeomNodes = {}
        
        # for every hotspot we store its bounds in the local space of each face
        self.hotspotsFaceBounds = {}
        
        # for every hotspot we store a PNMImage which has been declared to act as an interaction mask.
        # i.e. places where the image is black define a non-interactive region
        self.hotspotsImageMasks = {}
        
        # the normal of each face, indexed by the face constant (e.g. PanoConstants.CBM_TOP_FACE) 
        self.faceNormals = {
                     PanoConstants.CBM_TOP_FACE    : (0.0, 0.0, -1.0),
                     PanoConstants.CBM_LEFT_FACE   : (1.0, 0.0, 0.0),
                     PanoConstants.CBM_BOTTOM_FACE : (0.0, 0.0, 1.0),
                     PanoConstants.CBM_RIGHT_FACE  : (-1.0, 0.0, 0.0),
                     PanoConstants.CBM_BACK_FACE   : (0.0, 1.0, 0.0),
                     PanoConstants.CBM_FRONT_FACE  : (0.0, -1.0, 0.0)
        }
        
        # AABBs of the cube's faces.
        # indexed by the face constant (e.g. PanoConstants.CBM_TOP_FACE) and contains a tuple containing the min and max points each as a tuble
        # e.g: 
        #    minTop, maxTop = self.facesAABBs[PanoConstants.CBM_TOP_FACE]
        #    minx, miny, minz = minTop        
        self.facesAABBs = {}                

        # the root of the scene
        self.sceneRoot = None 

        # parent all debug geometries
        self.debugGeomsParent = None 

        # if true then self.debugGeomsParent will be visible
        self.vizDebugGeoms = False

        # parent all hotspots collision geometries
        self.collisionsGeomsParent = None
        
        # the texture cards for sprites rendering are descendants of this node
        self.spritesParent = None                  
        
        # sprites in format {hotspot_name : (<spriteRenderInterface instance>)}
        self.spritesByHotspot = {}  
                
        # used for detecting the hotspot under a window coordinate
        self.raycaster = None
        
        self.spritesEngine = spriteEngine
        

    def initialize(self):        

        # creates the root node 
        self.sceneRoot = render.attachNewNode(PanoConstants.NODE_ROOT_NODE)
        self.debugGeomsParent = self.sceneRoot.attachNewNode(PanoConstants.NODE_DEBUG_GEOMS_PARENT)
        self.debugGeomsParent.hide()
        self.collisionsGeomsParent = self.sceneRoot.attachNewNode(PanoConstants.NODE_COLLISIONS_GEOMS_PARENT)
        self.collisionsGeomsParent.hide()
        self.spritesParent = self.sceneRoot.attachNewNode(PanoConstants.NODE_SPRITES_PARENT)
        
        self.raycaster = NodeRaycaster(self)
        self.raycaster.initialize()
        
        # we want perspective
        # TODO: modify view parameters per node and in real-time
        lens = PerspectiveLens()
        lens.setFar(10000)
        lens.setFocalLength(1)
        base.cam.node().setLens(lens)

        self.loadCubeModel()        


    def dispose(self):
        '''
        Disposes any rendering resources, it assumes that this instance won't be used again.
        '''
        if self.raycaster is not None:
            self.raycaster.dispose()
            
        self.clearScene()
        
        if self.sceneRoot is not None:
            self.sceneRoot.removeNode()
            self.sceneRoot = None


    def loadCubeModel(self):   
        """
        Loads the egg file that contains the cube model for displaying the cubic
        panorama. 
        After loading it extracts references to the faces' textures in order to alter
        the in-game. It also measures the dimensions of the cubemap after taking into
        account the faces' dimensions as specified in the .egg file, the model scale applied
        by the model creator and finally the scale set on the respective nodepath.
        
        Conventions: 
            a) The name of the cube model must be 'cubemap.egg'.
            b) The names of the geoms definitions inside the .egg file must be: 
               top, left, bottom, right, back, front
            c) The model scale must be 1, 1, 1        
        """                
        self.cmap = self.resources.loadModel('cubemap.egg')
        self.cmap.setName(PanoConstants.NODE_CUBEMAP)
        self.cmap.reparentTo(self.sceneRoot)
        self.cmap.hide()
        self.cmap.setScale(10, 10, 10)  # scale up a bit the numbers for precision
        self.cmap.setPos(0,0,0)
        
        # disable depth write for the cube map
        self.cmap.setDepthWrite(False)    
        self.cmap.setDepthTest(False)
        self.cmap.setBin("fixed", PanoConstants.RENDER_ORDER_CUBEMAP)
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug(self.cmap.ls())

        self.faceDim = 2.0 * self.cmap.getScale()[0]        
        self.faceHalfDim = self.cmap.getScale()[0]          
        
        self.facesAABBs = {
                           PanoConstants.CBM_FRONT_FACE  : ((-self.faceHalfDim, self.faceHalfDim, -self.faceHalfDim), (self.faceHalfDim, self.faceHalfDim, self.faceHalfDim)), 
                           PanoConstants.CBM_BACK_FACE   : ((-self.faceHalfDim, -self.faceHalfDim, -self.faceHalfDim), (self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim)),
                           PanoConstants.CBM_RIGHT_FACE  : ((self.faceHalfDim, -self.faceHalfDim, -self.faceHalfDim), (self.faceHalfDim, self.faceHalfDim, self.faceHalfDim)),
                           PanoConstants.CBM_LEFT_FACE   : ((-self.faceHalfDim, -self.faceHalfDim, -self.faceHalfDim), (-self.faceHalfDim, self.faceHalfDim, self.faceHalfDim)),
                           PanoConstants.CBM_TOP_FACE    : ((-self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim), (self.faceHalfDim, self.faceHalfDim, self.faceHalfDim)),
                           PanoConstants.CBM_BOTTOM_FACE : ((-self.faceHalfDim, -self.faceHalfDim, -self.faceHalfDim), (self.faceHalfDim, self.faceHalfDim, -self.faceHalfDim))
                           }
                                        

        # caches references to the textures of each cubemap face
        for i, n in self.cubeGeomsNames.items():
            geomNode = self.cmap.find("**/Cube/=name=" + n)
            state = geomNode.node().getGeomState(0)
            self.facesGeomNodes[i] = geomNode.node()
             
                                    
        # builds matrices used in transforming points from/to world space and the faces' image space
        self.buildWorldToFaceMatrices() 
        
#        if self.log.isEnabledFor(logging.DEBUG):
#            self.log.debug('testing isFaceInFrustum from front: %d', self.isFaceInFrustum(PanoConstants.CBM_FRONT_FACE))
#            self.log.debug('testing isFaceInFrustum from back: %d', self.isFaceInFrustum(PanoConstants.CBM_BACK_FACE))
#            self.log.debug('testing isFaceInFrustum from left: %d', self.isFaceInFrustum(PanoConstants.CBM_LEFT_FACE))
#            self.log.debug('testing isFaceInFrustum from right: %d', self.isFaceInFrustum(PanoConstants.CBM_RIGHT_FACE))
#            self.log.debug('testing isFaceInFrustum from top: %d', self.isFaceInFrustum(PanoConstants.CBM_TOP_FACE))
#            self.log.debug('testing isFaceInFrustum from bottom: %d', self.isFaceInFrustum(PanoConstants.CBM_BOTTOM_FACE))
        
            
    def clearScene(self):
        '''
        Clears the scenegraph effectively removing all nodes from rendering.
        '''        
        self.debugGeomsParent.removeNode()            
        self.debugGeomsParent = self.sceneRoot.attachNewNode(PanoConstants.NODE_DEBUG_GEOMS_PARENT)
        if self.vizDebugGeoms:
            self.debugGeomsParent.show()
        else:
            self.debugGeomsParent.hide()
        
        self.collisionsGeomsParent.removeNode()
        self.collisionsGeomsParent = self.sceneRoot.attachNewNode(PanoConstants.NODE_COLLISIONS_GEOMS_PARENT)
        self.collisionsGeomsParent.hide()
        
        self.spritesParent.removeNode()
        self.spritesParent = self.sceneRoot.attachNewNode(PanoConstants.NODE_SPRITES_PARENT)        
        
        self.hotspotsFaceBounds = {}
        self.hotspotsImageMasks = {}
        
        self.cmap.hide()                   
        
        
    def getNode(self):
        """
        Returns the Node object that we are currently rendering.
        """
        return self.node

    
    def getSceneRoot(self):
        '''
        Returns the Nodepath that acts as the scene root.
        '''
        return self.sceneRoot
    
    
    def getCamera(self):
        '''
        Returns the NodePath of the camera that is used for rendering this node.
        '''
        return base.cam
    
    
    def render(self, millis):
        pass
    
        
    def displayNode(self, node):
        """
        Displays the given node.
        Convention: 
            The textures filenames of a node consist of a prefix that is
            the same as the node's name and the 6 postfixs, e.g.: _fr.jpg, _bk.jpg, _lt.jpg,
            _rt.jpg, _top.jpg and _bottom.jpg
        """        
        # do nothing if we are displaying this node already or reset the scene before displaying a new node
        if self.node is not None and self.node.name == node.name:
            return
        else:
            self.clearScene()                    
            
        self.node = node
                           
                    
        # load the cubemap or the background image        
        self._replaceCubemapTextures()
                
        # creates hotspot collision geometries and sprites
        self._createHotspotsGeoms()
        
        self.cmap.show()
                             
        
    def buildWorldToFaceMatrices(self):
        """
        Builds the 4x4 matrices that transform a point from the world coordinates system to the faces' image space.
        The image space has:
            a. Its origin at the top left corner of the face.
            b. The positive x axis running from left to right along the face.
            c. The positive y axis running from top to bottom along the face.
            d. Extends between [0.0, 1.0] inside the boundary of the face. 
        """
        facesCoords = {
                       PanoConstants.CBM_FRONT_FACE: (-self.faceHalfDim, self.faceHalfDim, self.faceHalfDim, 1, 0, -1), 
                       PanoConstants.CBM_BACK_FACE: (self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim, -1, 0, -1), 
                       PanoConstants.CBM_RIGHT_FACE: (self.faceHalfDim, self.faceHalfDim, self.faceHalfDim, 0, -1, -1), 
                       PanoConstants.CBM_LEFT_FACE: (-self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim, 0, 1, -1), 
                       PanoConstants.CBM_TOP_FACE: (-self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim, 1, 1, 0), 
                       PanoConstants.CBM_BOTTOM_FACE: (-self.faceHalfDim, self.faceHalfDim, -self.faceHalfDim, 1, -1, 0)
        }
        for face, coords in facesCoords.items():
            matOffset = Mat4()
            matOffset.setTranslateMat(VBase3(-coords[0], -coords[1], -coords[2]))
            matScale = Mat4()
            matScale.setScaleMat(VBase3(coords[3] / self.faceDim, coords[4] / self.faceDim, coords[5] / self.faceDim))
            self.worldToFaceMatrices[face] = matOffset * matScale
                
            # when calculating the inverse we will need to divide by the scale, so take care to replace zeros with ones                    
            scale = [ coords[3], coords[4], coords[5] ]
            for i in range(0, 3):
                if scale[i] == 0.0: scale[i] = 1
                                    
            matInvOffset = Mat4()
            matInvOffset.setTranslateMat(VBase3(coords[0], coords[1], coords[2]))
            matInvScale = Mat4()
            matInvScale.setScaleMat(VBase3(self.faceDim / scale[0], self.faceDim / scale[1], self.faceDim / scale[2]))
            self.faceToWorldMatrices[face] = matInvScale * matInvOffset
 
            
    def _createHotspotsGeoms(self):
        """
        Creates nodes for the collision geometry (a box) and the sprite.
        """
        for hp in self.node.getHotspots():            
            self.renderHotspot(hp)        
            self.createHotspotCollisionGeom(hp)
            self.renderHotspotDebugGeom(hp)
            
            if hp.clickMask is not None:
                img = self.resources.loadImage(hp.clickMask)
                if img:
                    self.hotspotsImageMasks[hp.name] = img
                      
                    
    def getHotspotSprite(self, hotspot):
        """
        Returns a SpriteRenderInterface which can be used to control the hotspot's sprite.
        
        @param hotspot: The hotspot instance
        @return: A SpriteRenderInterface instance or None.
        """        
        return self.spritesByHotspot.get(hotspot.name)                    
                    
            
    def renderHotspot(self, hp, spriteOverride = None):
        '''
        Setups node for rendering the sprite associated with this hotspot.
        While the details of creating the sprite nodes are hidden in addSprite, we still have
        to align the returned node with the surface covered by the hotspot in world space.
        @param hp: The hotspot to render. 
        @param sprite: If not None it is used for overriding the hotspot's sprite.
        '''        
        spriteName = hp.sprite if spriteOverride is None else spriteOverride
        if spriteName is not None:
            sprite = self.resources.loadSprite(spriteName)
            if sprite is None:
                self.log.error("Failed to add sprite %s because it wasn't found")
                return
            
            nodePath = SpritesUtil.createSprite3D(self.resources, sprite, self.spritesParent)                                    
            
            # gets position of hotspot's center in world space
            dim = self.getFaceTextureDimensions(hp.face)
            n = self.faceNormals[hp.face]
            t1 = (hp.xo + hp.width / 2.0) / dim[0]
            t2 = (hp.yo + hp.height / 2.0) / dim[1]
            centerPos = self.getWorldPointFromFacePoint(hp.face, (t1, t2))
            
            # align nodePath's center with the hotspot's                
            nodePath.setPos(VBase3(centerPos[0], centerPos[1], centerPos[2])) # + VBase3(n[0], n[1], n[2]) * 0.001)                
            
            # scale appropriately to cover the hotspot                
            nodePath.setScale(hp.width * self.faceDim / dim[0], 1.0, hp.height * self.faceDim / dim[1])
            
            # to orient it, we will align the center point with a point at a small distance along the face normal
            lookAt = centerPos - VBase3(n[0], n[1], n[2])
            nodePath.lookAt(lookAt[0], lookAt[1], lookAt[2])                         
                            
            if not hp.active:
                nodePath.hide()
                
            self.log.debug('adding hotspot %s' % hp.name)
            self.spritesByHotspot[hp.name] = SpriteRenderInterface(nodePath)          


    def createHotspotCollisionGeom(self, hp):
        '''
        Creates a collision box that covers the hotspot's interactive area in order to be able to detect a hotspot
        by raycasting from the mouse position.
        '''
        dim = self.getFaceTextureDimensions(hp.face)            
                
        # get world space coords of top left corner
        t1 = hp.xo / dim[0]
        t2 = hp.yo / dim[1]
        topLeft = self.getWorldPointFromFacePoint(hp.face, (t1, t2))
        
        # get world space coords of top right corner
        t1 = hp.xe / dim[0]
        t2 = hp.yo / dim[1]
        topRight = self.getWorldPointFromFacePoint(hp.face, (t1, t2))
        
        # get world space coords of bottom right corner
        t1 = hp.xe / dim[0]
        t2 = hp.ye / dim[1]
        bottomRight = self.getWorldPointFromFacePoint(hp.face, (t1, t2))
        
        # get world space coords of bottom left corner
        t1 = hp.xo / dim[0]
        t2 = hp.ye / dim[1]
        bottomLeft = self.getWorldPointFromFacePoint(hp.face, (t1, t2))
        
#        polygon = CollisionPolygon(topLeft, bottomLeft, bottomRight, topRight)
        polygon = CollisionPolygon(topLeft, topRight, bottomRight, bottomLeft)
                
        # name it as the hotspot, it will be convenient for raycasting
        cn = CollisionNode(hp.name)
        cn.addSolid(polygon)
        
        collisionNP = NodePath(cn)
        collisionNP.setName(hp.name)        
        collisionNP.reparentTo(self.collisionsGeomsParent)
                
        if not hp.active:
            collisionNP.hide()
        else:
            collisionNP.show()
        

    def renderHotspotDebugGeom(self, hp):
        '''
        Creates a box that covers the hotspot's boundaries in order to indicate its position
        and scale in the scene.
        '''
        dim = self.getFaceTextureDimensions(hp.face)            
        
        # get world space coords of top left corner
        t1 = hp.xo / dim[0]
        t2 = hp.yo / dim[1]
        wo = self.getWorldPointFromFacePoint(hp.face, (t1, t2))        
        
        # get world space coords of bottom right corner
        t3 = hp.xe / dim[0]
        t4 = hp.ye / dim[1]
        we = self.getWorldPointFromFacePoint(hp.face, (t1, t2))
        
        # store the face local bounds, useful for raycasting
        self.hotspotsFaceBounds[hp.name] = [t1, t2, t3, t4]
        
        box = self.resources.loadModel('box.egg') 
        box.setName('debug_' + hp.name)
        
        # we want to set as the position of our box, the respective world space position of the leftmost top corner of the hotspot
        # because image space and world space X and Y axis may have opposite directions, we use min() to choose correctly between
        # wo and we elements for setPos(): since the leftmost top corner has the smallest coordinates in image space, it will follow
        # suite in the world space as well.
        box.setPos(min(wo[0], we[0]), min(wo[1], we[1]), min(wo[2], we[2]))    
        box.setScale(
                     max(0.2, math.fabs(we[0] - wo[0])), 
                     max(0.2, math.fabs(we[1] - wo[1])), 
                     max(0.2, math.fabs(we[2] - wo[2])))   
                             
        box.setDepthTest(False)
        box.setDepthWrite(False)                    
        box.setBin("fixed", PanoConstants.RENDER_ORDER_DEBUG_GEOMS)
        
        box.setRenderModeWireframe()                                        
        box.reparentTo(self.debugGeomsParent)
            
            
    def drawDebugHotspots(self, flag):
        self.vizDebugGeoms = flag
        if flag:
            self.debugGeomsParent.show()
        else:
            self.debugGeomsParent.hide()
            
            
    def removeHotspot(self, hotspot):
        '''
        Removes a hotspot from the render list. The debug geometry and sprite associated with the hotspot
        won't be visible anymore.
        @param hotspot: A pano.model.Hotspot instance for the hotspot to be removed.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Removing hotspot %s' % hotspot.name)
            
        spr = self.getHotspotSprite(hotspot)
        if spr is not None:
            spr.remove()
            del self.spritesByHotspot[hotspot.name]                

        # remove the hotspot's debug geometry
        if self.debugGeomsParent is not None:
            np = self.debugGeomsParent.find('debug_' + hotspot.name)
            if np != None and not np.isEmpty():
                np.removeNode()
                
        # remove the collision geometry
        if self.collisionsGeomsParent is not None:
            np = self.collisionsGeomsParent.find(hotspot.name)
            if np != None and not np.isEmpty():
                np.removeNode()


    def hideHotspot(self, hp):
        '''
        Hides the scene node that parents the hotspots sprite in the scene.
        @param hp: The hotspot that will be hidden. 
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Hiding hotspot %s' % hp.name)
                
        sri = self.getHotspotSprite(hp)
        if sri is not None:
            sri.hide()
            
        # remove the collision geometry while the hotspot is hidden
        if self.collisionsGeomsParent is not None:
            np = self.collisionsGeomsParent.find(hp.name)
            if np != None and not np.isEmpty():
                np.removeNode()


    def showHotspot(self, hp):
        '''
        Shows the scene node that parents the hotspots sprite in the scene.
        @param hp: The hotspot that will be shown. 
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Showing hotspot %s' % hp.name)
        
        sri = self.getHotspotSprite(hp)
        if sri is not None:
            sri.show()
            
        # create again the collision geometry
        self.createHotspotCollisionGeom(hp)


    def replaceHotspotSprite(self, hotspot, newSprite):
        '''
        Changes the visual appearance of a hotspot by replacing its sprite with a new one.
        @param hp: The hotspot that will have its sprite replaced.
        @param newSprite: The name of the new sprite to use for rendering.  
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Replacing hotspot's %s sprite with %s" % (hotspot.name, newSprite))
        self.removeHotspot(hotspot)
        self.renderHotspot(hotspot, newSprite)
        self.renderHotspotDebugGeom(hotspot) 
                    
    
    def pauseAnimations(self):
        """
        Stops all node animations.
        """
        for sri in self.spritesByHotspot.values():
            sri.pause()


    def resumeAnimations(self):
        """
        Resumes node animations.
        """
        for sri in self.spritesByHotspot.values():
            sri.play()
            
            
    def raycastHotspots(self, x, y):
        '''
        Returns the hotspot under the given window coordinates.
        @param x: The x window coordinate in render space.
        @param y: The y window coordinate in render space.
        @return: A list of Hotspot instances that were found under the window point. The hotspots are ordered
        by their depth from the camera. 
        '''                
        self.collisionsGeomsParent.show()        
        hotspots = []
        results = self.raycaster.raycastWindow(x, y, True)        
        if results is not None:
            for np, pt in results:                
                hp = self.node.getHotspot(np.getName())
                if hp is not None:
                                                            
                    # we have a hotspot but perhaps its click mask, if any, will reject that point
                    # the mask should have the same dimensions with the hotspot's rectangular interaction area
                    maskImg = self.hotspotsImageMasks.get(hp.name)
                    if maskImg is not None:
                        bounds = self.hotspotsFaceBounds[hp.name]
                        facePoint = self.getFaceLocalCoords(hp.face, pt)                        
                        hotspotRelativePoint = [(facePoint[0] - bounds[0]) / (bounds[2] - bounds[0]), (facePoint[1] - bounds[1]) / (bounds[3] - bounds[1])]
                        hotspotRelativePoint[0] *= maskImg.getXSize()
                        hotspotRelativePoint[1] *= maskImg.getYSize()
                        col = maskImg.getXel(int(hotspotRelativePoint[0]), int(hotspotRelativePoint[1]))                    
                        if col[0] == 0.0 and col[1] == 0.0 and col[2] == 0.0:                            
                            continue                        
                            
                    hotspots.append(hp)
                 
        self.collisionsGeomsParent.hide()
        
#        self.log.debug("------------------------")
#        for hp in hotspots:
#            self.log.debug('raycasted hotspot %s' % hp.name)
#        self.log.debug("------------------------")
#            
        return hotspots                       
            
    
    def getFaceLocalCoords(self, face, p):    
        """
        Translates the given world space point in the local 2D coordinate system
        of the specified face. The local space extends in [0..1] in the vertical
        and horizontal axis, thus the method returns a tuple of x, y values in the
        [0..1] range.
        """
        
#        if self.log.isEnabledFor(logging.DEBUG):
#            self.log.debug('getFaceLocalCoords for point %s', p)    
        mat = self.worldToFaceMatrices[face]        
        fp = mat.xformPoint(p)
        
#        if self.log.isEnabledFor(logging.DEBUG):        
#            self.log.debug('face point is %s while inversed transformed back to world is %s', str(fp), str(self.faceToWorldMatrices[face].xformPoint(fp)))
        if fp.getX() < NodeRenderer.EPSILON_POS:
            return (fp.getY(), fp.getZ())
        elif fp.getY() < NodeRenderer.EPSILON_POS:
            return (fp.getX(), fp.getZ())
        else:
            return (fp.getX(), fp.getY()) 


    def getWorldPointFromFacePoint(self, face, p):
        """
        The point p is given in the local 2D coordinate system of the specified face. This local space extends 
        in [0..1] in the vertical and horizontal axis, thus the method returns a tuple of x, y values in the
        [0..1] range.
        Returns a VBase3 with the world space coordinates.
        """
        dim = self.getFaceTextureDimensions(face)
        m = self.faceToWorldMatrices[face]
        n = self.faceNormals[face]
        
        if math.fabs(n[0]) < NodeRenderer.EPSILON_POS and math.fabs(n[1]) < NodeRenderer.EPSILON_POS:        
            return m.xformPoint(VBase3(p[0], p[1], 0.0))
        elif math.fabs(n[0]) < NodeRenderer.EPSILON_POS and math.fabs(n[2]) < NodeRenderer.EPSILON_POS:
            return m.xformPoint(VBase3(p[0], 0.0, p[1]))
        else:
            return m.xformPoint(VBase3(0.0, p[0], p[1]))           
        
        
    def getHotspotWorldPos(self, hotspot):
        # gets position of hotspot's center in world space
        dim = self.getFaceTextureDimensions(hotspot.face)
        n = self.faceNormals[hotspot.face]
        t1 = (hotspot.xo + hotspot.width / 2.0) / dim[0]
        t2 = (hotspot.yo + hotspot.height / 2.0) / dim[1]
        centerPos = self.getWorldPointFromFacePoint(hotspot.face, (t1, t2))
        return centerPos               

    
    def findFaceFromNormal(self, n):
        """
          Finds the face of the cubemap on which lies the given normal vector.

          This is done by finding the coordinate of the normal with the greatest
          absolute value and finally considering the sign.
          If x is the greatest coordinate, then the normal points either to the left
          or right. If the sign is positive, then the normal points to the right, while
          if it is negative it points to the left. Similarly for the rest coordinates.
        """
        abs_x = abs(n.getX())
        abs_y = abs(n.getY())
        abs_z = abs(n.getZ())
        if abs_x < abs_y or abs_x < abs_z:
            if abs_y > abs_z:
                if n.getY() > 0:    
                    return PanoConstants.CBM_BACK_FACE
                else:    
                    return PanoConstants.CBM_FRONT_FACE
            else:
                if n.getZ() > 0:    
                    return PanoConstants.CBM_BOTTOM_FACE
                else:    
                    return PanoConstants.CBM_TOP_FACE
        else:
            if n.getX() > 0:    
                return PanoConstants.CBM_LEFT_FACE
            else:    
                return PanoConstants.CBM_RIGHT_FACE            
    
    
    def isFaceInFrustum(self, face):
        """
        Returns True if the given face passes the frustum culling check.
        It works by accessing the vertex data of the face and for each vertex it evaluates
        each of the frustum's planes equations and if a single vertex yields a positive result
        then the face is considered inside the frustum.
        """
        
        if face != PanoConstants.CBM_TOP_FACE and face != PanoConstants.CBM_BOTTOM_FACE:        
            # read camera's heading angle
            camHeading = base.camera.getH()
            
            if self.log.isEnabledFor(logging.DEBUG):                         
                self.log.debug('camHeading: %f', camHeading)
            
            if (camHeading < 90.0 or camHeading > 270.0) and face == PanoConstants.CBM_FRONT_FACE:
                return True
            
            if (camHeading < 180.0 and camHeading > 0.0) and face == PanoConstants.CBM_LEFT_FACE:
                return True
            
            if camHeading > 180.0 and face == PanoConstants.CBM_RIGHT_FACE:
                return True
            
            if camHeading < 270.0 and camHeading > 90.0 and face == PanoConstants.CBM_BACK_FACE:
                return True
        else:
            camPitch = base.camera.getP()
            if self.log.isEnabledFor(logging.DEBUG): 
                self.log.debug('camPitch: %f', camPitch)
            
            aspect = 1.0 / base.camLens.getAspectRatio()
            pitchLimit = (180.0 /math.pi) * math.atan(aspect*0.5)
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('pitchLimit: %f', pitchLimit)
            
            if camPitch > pitchLimit and camPitch < 180.0 and face == PanoConstants.CBM_TOP_FACE:
                return True
            
            if camPitch > 270.0 and camPitch < (360.0 - pitchLimit) and face == PanoConstants.CBM_BOTTOM_FACE:
                return True
            
        return False


    def getFaceTextureDimensions(self, face):
        """
        Returns a tuple containing the width and height of the cubemap textures.
        tuple[0] holds the width while tuple[1] holds the height of the textures.
        """
        if self.facesGeomNodes.has_key(face):
            # for Panda 1.5.4
#            tex = self.facesGeomNodes[face].getGeomState(0).getTexture().getTexture()

            # for Panda 1.6
            rs = self.facesGeomNodes[face].getGeomState(0)
            ta = rs.getAttrib(TextureAttrib.getClassType())
            if ta is not None:
                tex = ta.getTexture()
                
                if tex is not None:
                    return (tex.getXSize(), tex.getYSize())
            
        return (0, 0)             


    def _replaceCubemapTextures(self):
        
        prefixFilename = self.node.getCubemap()
        ext = self.node.getExtension() if self.node.getExtension() is not None else 'png'
        faceCodes = { 
                     PanoConstants.CBM_FRONT_FACE : '_fr.' + ext,
                     PanoConstants.CBM_BACK_FACE : '_bk.' + ext,
                     PanoConstants.CBM_LEFT_FACE : '_lt.' + ext,
                     PanoConstants.CBM_RIGHT_FACE : '_rt.' + ext,
                     PanoConstants.CBM_TOP_FACE : '_top.' + ext,
                     PanoConstants.CBM_BOTTOM_FACE : '_bt.' + ext
                     }
        
        for face, suffix in faceCodes.items():
            self.setFaceTexture(face, prefixFilename + suffix)


    def setFaceTexture(self, face, filename):
        '''
        Sets the texture of the specified face of the cubemap.        
        '''    
        tex = self.resources.loadTexture(filename)
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)        
        rs = self.facesGeomNodes[face].getGeomState(0).setAttrib(TextureAttrib.make(tex))
        self.facesGeomNodes[face].setGeomState(0, rs)


    
    
