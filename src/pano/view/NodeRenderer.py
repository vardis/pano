import os
import math
import logging

from pandac.PandaModules import Texture
from pandac.PandaModules import TextureAttrib, CullFaceAttrib
from pandac.PandaModules import GeomVertexReader
from pandac.PandaModules import LineSegs
from pandac.PandaModules import Filename
from direct.showbase.PythonUtil import *
from pandac.PandaModules import Mat4, VBase3

from constants import PanoConstants

# Check these two posts:
# http://www.panda3d.net/phpbb2/viewtopic.php?t=2022&highlight=projection
# http://www.panda3d.net/phpbb2/viewtopic.php?t=851&highlight=skybox
class NodeRenderer:

    FRUSTUM_NEAR   = 0
    FRUSTUM_FAR    = 1
    FRUSTUM_RIGHT  = 2
    FRUSTUM_LEFT   = 3
    FRUSTUM_TOP    = 4
    FRUSTUM_BOTTOM = 5

    EPSILON_POS = 0.000001

    def __init__(self, resources):   
                   
        self.log = logging.getLogger('pano.render')     

        self.resources = resources
        
        #The node that is displayed
        self.node = None
        
        #The common dimension of the square faces of the cubemap
        self.faceDim = 0
        self.faceHalfDim = 0
        
        #The cubemap model
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
            a) There exists a convention that the name of the cube model must be 'cubemap.egg'.
            b) The names of the geoms definitions inside the .egg file must be: 
               top, left, bottom, right, back, front
            c) The model scale must be 1, 1, 1        
        """        
        modelPath = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, 'cubemap-linux.egg')
        self.cmap = loader.loadModel(modelPath)
        self.cmap.setName('cmap')
        self.cmap.reparentTo(render)
        self.cmap.setScale(10, 10, 10)
        self.cmap.setPos(0,0,0)
        
        self.debugGeomsParent = self.cmap.attachNewNode('debug_geoms')
        
        self.spritesParent = self.cmap.attachNewNode('sprites_tex_cards')
        
        # Disable depth write for the cube map
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

        for i, n in self.cubeGeomsNames.items():
            geomNode = self.cmap.find("**/Cube/=name=" + n)
            state = geomNode.node().getGeomState(0)                 
            tex = state.getAttrib(TextureAttrib.getClassType()).getTexture()
            self.faceTextures[i] = tex 
                                    
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
        # remove and destroy debug geometries
        debugGeoms = self.debugGeomsParent.getChildrenAsList()            
        for box in debugGeoms:
            box.removeNode()
            
        # same for hotspots        
        hotspots = self.spritesParent.getChildrenAsList()            
        for hp in hotspots:
            hp.removeNode()
        
        
    def displayNode(self, node):
        """
        Displays the given node.
        Convention: The textures filenames of a node consist of a prefix that is
        the same as the node's name and the 6 postfixs: _fr.jpg, _bk.jpg, _lt.jpg,
        _rt.jpg, _top.jpg and _bottom.jpg
        """
        if self.node is not None and self.node.getName() == node.getName():
            return
        else:
            self.initScene()
            
        self.node = node        
        
        # load the 6 textures of the node        
        prefixFilename = self.node.getCubemap()
        
        self.log.debug('full path to resource: %s', self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_fr.jpg'))
        filename = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, prefixFilename + '_fr.jpg')        
        self.faceTextures[PanoConstants.CBM_FRONT_FACE].read(Filename(filename))
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
        
        # setup hotspot sprites, if any
        self.createHotspotsTextureCards()
                    
        print self.cmap.ls()
                     
        
    def buildWorldToFaceMatrices(self):
        """
        Builds the 4x4 matrices that transform a point from the world coordinates system
        to the system that has its origin at the centre of a face, has the positive x axis running left to right
        along the face, has the positive y axis running top to bottom along the face and extends between [0.0, 1.0]
        inside the boundary of the face. 
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
        if flag and self.node is not None:
            for hp in self.node.getHotspots():
                tex = self.faceTextures[hp.getFace()]            
                mat = self.faceToWorldMatrices[hp.getFace()]
                
                fo = VBase3(hp.getXo() / tex.getXSize(), 0.0, hp.getYo() / tex.getYSize())
                wvo = mat.xformPoint(fo) 
                
                fe = VBase3(hp.getXe() / tex.getXSize(), 0.0, hp.getYe() / tex.getYSize())
                wve = mat.xformPoint(fe)                                                 
                                
                box = loader.loadModel(self.resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, 'box.egg.pz'))
#                box = loader.loadModelCopy('/c/Documents and Settings/Fidel/workspace/Panorama/demo/data/models/box.egg.pz')                
                
                box.setName('debug_geom_' + hp.getName())
                box.setPos(wvo[0], wvo[1], wve[2])
                box.setScale(
                             max(0.1, math.fabs(wve[0] - wvo[0])), 
                             max(0.1, math.fabs(wve[1] - wvo[1])), 
                             max(0.1, math.fabs(wve[2] - wvo[2])))                
                box.setRenderModeWireframe()                                
                box.reparentTo(self.debugGeomsParent)
            
        elif flag:
            debugGeoms = self.debugGeomsParent.getChildrenAsList()            
            for box in debugGeoms:
                box.removeNode()
            
    def createHotspotsTextureCards(self):
        for hp in self.node.getHotspots():
            if hp.sprite is not None:
                sprite = self.resources.loadSprite(hp.sprite)
                if sprite.eggFile is not None:
                    eggPath = self.resources.getResourceFullPath(PanoConstants.RES_TYPE_MODELS, sprite.eggFile)
                    textureCard = loader.loadModel(eggPath)
                    textureCard.reparentTo(self.spritesParent)
                    # get position of hotspot's center in world space
                    dim = self.getFaceTextureDimensions(hp.getFace())
                    n = self.faceNormals[hp.getFace()]
                    t1 = (hp.xo + hp.width / 2.0) / dim[0]
                    t2 = (hp.yo + hp.height / 2.0) / dim[1]
                    print 't1: ', t1, ' t2: ', t2
                    worldPos = self.getWorldPointFromFacePoint(hp.getFace(), (t1, t2))
                    # align textureCard's center with hotspots, now the texture card still faces along -Y
                    textureCard.setPos(VBase3(worldPos[0], worldPos[1], worldPos[2]) + VBase3(n[0], n[1], n[2]) * 0.01)
                    # scale appropriately
                    textureCard.setScale(hp.width * self.faceDim / dim[0], 1.0, hp.height * self.faceDim / dim[1])
                    # orient the textureCard using the normal, we will align the center point with a point at a small
                    # distance along the face normal
                    lookAt = worldPos - VBase3(n[0], n[1], n[2])
                    textureCard.lookAt(lookAt[0], lookAt[1], lookAt[2])

        
            
    """
    Translates the given world space point in the local 2D coordinate system
    of the specified face. The local space extends in [0..1] in the vertical
    and horizontal axis, thus the method returns a tuple of x, y values in the
    [0..1] range.
    """
    def getFaceLocalCoords(self, face, p):    
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('getFaceLocalCoords for point %s', p)    
        mat = self.worldToFaceMatrices[face]        
        fp = mat.xformPoint(p)
        
        if self.log.isEnabledFor(logging.DEBUG):        
            self.log.debug('face point is %s while inversed transformed back to world is %s', str(fp), str(self.faceToWorldMatrices[face].xformPoint(fp)))
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

    """
      Finds the face of the cubemap on which lies the given normal vector.

      This is done by finding the coordinate of the normal with the greatest
      absolute value and finally considering the sign.
      If x is the greatest coordinate, then the normal points either to the left
      or right. If the sign is positive, then the normal points to the right, while
      if it is negative it points to the left. Similarly for the rest coordinates.
    """
    def findFaceFromNormal(self, n):
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

    """
    Returns the NodePath of the cubemap model.
    """
    def nodepath(self):
        return self.cmap
    
    
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
        if self.faceTextures.has_key(face):
            tex = self.faceTextures[face]
            if tex is not None:
                return (tex.getXSize(), tex.getYSize())
            
        return (0, 0)             
    
    
