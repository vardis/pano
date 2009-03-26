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

import os
import math
import logging

from pandac.PandaModules import Texture, NodePath
from pandac.PandaModules import TextureAttrib, CullFaceAttrib
from pandac.PandaModules import GeomVertexReader
from pandac.PandaModules import LineSegs
from pandac.PandaModules import Filename
from direct.showbase.PythonUtil import *
from pandac.PandaModules import Mat4, VBase3

from constants import PanoConstants
from view.VideoPlayer import VideoPlayer
from view.sprites import *

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

    def __init__(self, resources):   
                   
        self.log = logging.getLogger('pano.render')     

        self.resources = resources
        
        self.videoPlayer = VideoPlayer('hotspots_player', resources)
        
        # the game node that we are rendering
        self.node = None
        
        # the dimension of the cubemap
        self.faceDim = 0
        self.faceHalfDim = 0
        
        # our root node 
        self.rootNode = None
        
        # the node that hosts the cubemap model
        self.cmap = None
        
        # contains all the sprites in (sprite-node-name, sprite-nodepath) key,value pairs
        self.sprites = {}
        
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
        self.faceTextures = { }
        
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
        
        # the parent scenegraph node of the hotspots debug geometries
        self.debugGeomsParent = None
        
        # if True then the debug geometries for the hotspots will be drawn
        self.drawHotspots = False
        
        # the texture cards for sprites rendering are descedants of this node
        self.spritesParent = None

    
    def initialize(self):
        # creates the root node 
        self.rootNode = render.attachNewNode(PanoConstants.NODE_ROOT_NODE)
        
        base.camLens.setFar(100000)
        base.camLens.setFocalLength(1)
        self.loadCubeModel()
        
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
        modelPath = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, 'cubemap-linux.egg')
        self.cmap = loader.loadModel(modelPath)
        self.cmap.setName(PanoConstants.NODE_CUBEMAP)
        self.cmap.reparentTo(self.rootNode)
        self.cmap.hide()
        self.cmap.setScale(10, 10, 10)  # scale up a bit the numbers for precision
        self.cmap.setPos(0,0,0)
        
        
        
        # disable depth write for the cube map
        self.cmap.setDepthWrite(False)    
        
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
                                
        print self.cmap.ls()

        # caches references to the textures of each cubemap face
        for i, n in self.cubeGeomsNames.items():
            geomNode = self.cmap.find("**/Cube/=name=" + n)
            state = geomNode.node().getGeomState(0)                 
            tex = state.getAttrib(TextureAttrib.getClassType()).getTexture()
            self.faceTextures[i] = tex 
                                    
        # builds matrices used in transforming points from/to world space and the faces' image space
        self.buildWorldToFaceMatrices() 
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('testing isFaceInFrustum from front: %d', self.isFaceInFrustum(PanoConstants.CBM_FRONT_FACE))
            self.log.debug('testing isFaceInFrustum from back: %d', self.isFaceInFrustum(PanoConstants.CBM_BACK_FACE))
            self.log.debug('testing isFaceInFrustum from left: %d', self.isFaceInFrustum(PanoConstants.CBM_LEFT_FACE))
            self.log.debug('testing isFaceInFrustum from right: %d', self.isFaceInFrustum(PanoConstants.CBM_RIGHT_FACE))
            self.log.debug('testing isFaceInFrustum from top: %d', self.isFaceInFrustum(PanoConstants.CBM_TOP_FACE))
            self.log.debug('testing isFaceInFrustum from bottom: %d', self.isFaceInFrustum(PanoConstants.CBM_BOTTOM_FACE))
        
    def getNode(self):
        """
        Returns the Node object that we are currently rendering.
        """
        return self.node

        
    def render(self, millis):
        pass
            
    def initScene(self):
        """
        Sets the scene to an initial state by destroying any rendering resources allocated that far
        for rendering the previously active node.
        """
        # remove and destroy debug geometries        
        if self.debugGeomsParent is not None:
            debugGeoms = self.debugGeomsParent.getChildrenAsList()            
            for box in debugGeoms:
                box.removeNode()
            self.debugGeomsParent.node().removeAllChildren()           
            self.debugGeomsParent.removeNode() 
            
        # same for hotspots        
        if self.spritesParent is not None:
            hotspots = self.spritesParent.getChildrenAsList()            
            for hp in hotspots:                
                if hp.hasPythonTag('video'):
                    video = hp.getPythonTag('video')
                    video.stop()
                hp.removeNode()
            self.spritesParent.node().removeAllChildren()
            self.spritesParent.removeNode()
            
        self.debugGeomsParent = self.cmap.attachNewNode(PanoConstants.NODE_DEBUG_GEOMS_PARENT)        
        self.spritesParent = self.cmap.attachNewNode(PanoConstants.NODE_SPRITES_PARENT)
            
        self.sprites.clear()
        
        
    def displayNode(self, node):
        """
        Displays the given node.
        Convention: 
            The textures filenames of a node consist of a prefix that is
            the same as the node's name and the 6 postfixs: _fr.jpg, _bk.jpg, _lt.jpg,
            _rt.jpg, _top.jpg and _bottom.jpg
        """
        
        # do nothing if we are displaying this node already or reset the scene before displaying a new node
        if self.node is not None and self.node.getName() == node.getName():
            return
        else:
            self.initScene()
            
        self.node = node        
        
# load the 6 textures of the node and assign them to the respective faces
       
        prefixFilename = self.node.getCubemap()

        self.log.debug('cwd: %s' % os.getcwd())

        path = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_fr.jpg')
        self.log.debug('full path to resource: %s', path)
        
        filename = '/c/Documents and Settings/Fidel/workspace/pano/demo/' + self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_fr.jpg')
        self.faceTextures[PanoConstants.CBM_FRONT_FACE] = self.resources.loadTexture(prefixFilename + '_fr.jpg')
        self.faceTextures[PanoConstants.CBM_FRONT_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_FRONT_FACE].setWrapV(Texture.WMClamp)
        
        filename = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_bk.jpg')
        self.faceTextures[PanoConstants.CBM_BACK_FACE].read(Filename(filename))
        self.faceTextures[PanoConstants.CBM_BACK_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_BACK_FACE].setWrapV(Texture.WMClamp)
        
        filename = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_lt.jpg')
        self.faceTextures[PanoConstants.CBM_LEFT_FACE].read(Filename(filename))
        self.faceTextures[PanoConstants.CBM_LEFT_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_LEFT_FACE].setWrapV(Texture.WMClamp)
        
        filename = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_rt.jpg')
        self.faceTextures[PanoConstants.CBM_RIGHT_FACE].read(Filename(filename))
        self.faceTextures[PanoConstants.CBM_RIGHT_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_RIGHT_FACE].setWrapV(Texture.WMClamp)
        
        filename = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_top.jpg')
        self.faceTextures[PanoConstants.CBM_TOP_FACE].read(Filename(filename))
        self.faceTextures[PanoConstants.CBM_TOP_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_TOP_FACE].setWrapV(Texture.WMClamp)
        
        filename = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_bt.jpg')
        self.faceTextures[PanoConstants.CBM_BOTTOM_FACE].read(Filename(filename))
        self.faceTextures[PanoConstants.CBM_BOTTOM_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_BOTTOM_FACE].setWrapV(Texture.WMClamp)
        
        # creates hotspot collision geometries and sprites
        self.createHotspotsGeoms()
        
        self.cmap.show()
        
        print self.cmap.ls()
                     
        
    def pauseAnimations(self):
        """
        Stops all node animations.
        """
        for np in self.sprites.values():
            if np.hasPythonTag('video'):
                video = np.getPythonTag('video')
                t = video.getTime()
                video.stop()
                video.setTime(t)
            else:
                seq = np.find('**/+SequenceNode').node()                
                seq.pose(seq.getFrame())           
            
    def resumeAnimations(self):
        """
        Resumes node animations.        
        """
        for np in self.sprites.values():
            if np.hasPythonTag('video'):
                video = np.getPythonTag('video')                
                video.play()                
            else:
                seq = np.find('**/+SequenceNode').node()
                seq.loop(False)                
        
    def buildWorldToFaceMatrices(self):
        """
        Builds the 4x4 matrices that transform a point from the world coordinates system to the faces' image space.
        The image space has:
            a. Its origin at the centre of a face.
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

    
    def drawDebugHotspots(self, flag):
        self.drawHotspots = flag
        if flag:
            self.debugGeomsParent.show()
        else:
            self.debugGeomsParent.hide()
            
    def createHotspotsGeoms(self):
        """
        Creates nodes for the collision geometry (a box) and the sprite.
        """
        for hp in self.node.getHotspots():
            
            dim = self.getFaceTextureDimensions(hp.getFace())
            
# create a box that covers the hotspot's boundaries in order to indicate its position
# and scale inside the world
                
            # get world space coords of top left corner
            t1 = hp.xo / dim[0]
            t2 = hp.yo / dim[1]
            wo = self.getWorldPointFromFacePoint(hp.getFace(), (t1, t2))
            
            # get world space coords of bottom right corner
            t1 = hp.xe / dim[0]
            t2 = hp.ye / dim[1]
            we = self.getWorldPointFromFacePoint(hp.getFace(), (t1, t2))
            
            box = loader.loadModel(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, 'box.egg.pz'))
            
            # we want to set as the position of our box, the respective world space position of the leftmost top corner of the hotspot
            # because image space and world space X and Y axis may have opposite directions, we use min() to choose correctly between
            # wo and we elements for setPos(): since the leftmost top corner has the smallest coordinates in image space, it will follow
            # suite in the world space as well.
            box.setPos(min(wo[0], we[0]), wo[1], min(wo[2], we[2]))
            box.setScale(
                         max(0.2, math.fabs(we[0] - wo[0])), 
                         max(0.2, math.fabs(we[1] - wo[1])), 
                         max(0.2, math.fabs(we[2] - wo[2])))                
            box.setRenderModeWireframe()                                
            box.reparentTo(self.debugGeomsParent)

# setups node for rendering the sprite associated with this hotspot
# while the details of creating the sprite nodes are hidden in addSprite, we still have
# to align the returned node with the surface covered by the hotspot in world space.                        
            if hp.sprite is not None:
                sprite = self.resources.loadSprite(hp.sprite)
                nodePath = self.addSprite(sprite)                
                
                # gets position of hotspot's center in world space
                dim = self.getFaceTextureDimensions(hp.getFace())
                n = self.faceNormals[hp.getFace()]
                t1 = (hp.xo + hp.width / 2.0) / dim[0]
                t2 = (hp.yo + hp.height / 2.0) / dim[1]
                centerPos = self.getWorldPointFromFacePoint(hp.getFace(), (t1, t2))
                
                # align nodePath's center with the hotspot's
                nodePath.setPos(VBase3(centerPos[0], centerPos[1], centerPos[2]) + VBase3(n[0], n[1], n[2]) * 0.01)                
                
                # scale appropriately to cover the hotspot
                nodePath.setScale(hp.width * self.faceDim / dim[0], 1.0, hp.height * self.faceDim / dim[1])
                
                # to orientate, we will align the center point with a point at a small distance along the face normal
                lookAt = centerPos - VBase3(n[0], n[1], n[2])
                nodePath.lookAt(lookAt[0], lookAt[1], lookAt[2])                    

    def addSprite(self, sprite):
        """
        Adds a sprite for rendering.
        If the sprite is animated, the animation will automatically begin from frame 1.
        To control the animation you must acquire the rendering interface for the sprite using the method
        NodeRenderer.getSpriteRenderInterface(spriteName).
        See sprites.SpriteRenderInterface for more details.
        
        Returns the NodePath that hosts the sprite inside the scenegraph.
        
        Note: You don't need to manually add the sprites of each hotspot of a game node as these
        are automatically added when you display the node.
        """
        nodeName = SpritesUtil.getSpriteNodeName(sprite.getName())
        nodePath = None
        if not self.sprites.has_key(nodeName):                    
            if sprite.getEggFile() is not None:
                nodePath = SpritesUtil.createImageSequenceSprite(self.resources, sprite, self.spritesParent)
            elif sprite.getVideo() is not None:
                nodePath = SpritesUtil.createVideoSprite(self.resources, sprite, self.spritesParent)
            
            nodePath.setName(nodeName)
            self.sprites[nodeName] = nodePath  
        return self.sprites[nodeName]                 
    
    def removeSprite(self, spriteName):
        """
        Removes the named sprite from rendering.
        """
        nodeName = SpritesUtil.getSpriteNodeName(spriteName)
        np = self.spritesParent.find(nodeName)
        if np is not None:
            np.removeNode()
            del self.sprites[nodeName]
    
    def getSpriteRenderInterface(self, spriteName):
        """
        Returns a SpriteRenderInterface which can be used to control various rendering aspects
        of the sprites, such as animation and visibility.
        """
        np = self.spritesParent.find(SpritesUtil.getSpriteNodeName(spriteName))
        if np is not None:
            return SpriteRenderInterface(np)
        else:
            return None
                
    
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
        The point p is given in the coordinate system that has its origin at the center of the face
        and extends from -1.0 to 1.0 from left to right for the x-axis and from top to bottom for the 
        y-axis.
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
        dim = self.getFaceTextureDimensions(hotspot.getFace())
        n = self.faceNormals[hotspot.getFace()]
        t1 = (hotspot.xo + hotspot.width / 2.0) / dim[0]
        t2 = (hotspot.yo + hotspot.height / 2.0) / dim[1]
        centerPos = self.getWorldPointFromFacePoint(hotspot.getFace(), (t1, t2))
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

    
    def nodepath(self):
        """
        Returns the NodePath of the cubemap model.
        """
        return self.cmap
    
    def getCamera(self):
        '''
        Returns the camera that is used for rendering this node.
        '''
        return base.camera
    
    
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
        if self.faceTextures.has_key(face):
            tex = self.faceTextures[face]
            if tex is not None:
                return (tex.getXSize(), tex.getYSize())
            
        return (0, 0)             
    
    
