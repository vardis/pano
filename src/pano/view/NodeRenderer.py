import os
import math

from pandac.PandaModules import Texture
from pandac.PandaModules import TextureAttrib
from pandac.PandaModules import GeomVertexReader
from pandac.PandaModules import Filename
from direct.showbase.PythonUtil import *
from pandac.PandaModules import Mat4, VBase3

from constants import PanoConstants

# Check these two posts:
# http://www.panda3d.net/phpbb2/viewtopic.php?t=2022&highlight=projection
# http://www.panda3d.net/phpbb2/viewtopic.php?t=851&highlight=skybox
class NodeRenderer:

    def __init__(self, resources):   
                
        self.resources = resources
        
        #The node that is displayed
        self.node = None
        
        #The common dimension of the square faces of the cubemap
        self.faceDim = 0
        self.faceHalfDim = 0
        
        #The cubemap model
        self.cmap = None
        
        # matricex that transform from world space to the faces' image space
        self.worldToFaceMatrices = {}
        
        #Stores the textures of the faces. E.g.:
        #frontTexture = self.faceTextures[CBM_FRONT_FACE]
        self.faceTextures = { }
        
        base.camLens.setFar(100000)
        base.camLens.setFocalLength(1)
        
        self.loadCubeModel()
        
    def getNode(self):
        """
        Returns the Node object that we are currently rendering.
        """
        return self.node

    def displayNode(self, node):
        """
        Displays the given node.
        Convention: The textures filenames of a node consist of a prefix that is
        the same as the node's name and the 6 postfixs: _fr.jpg, _bk.jpg, _lt.jpg,
        _rt.jpg, _top.jpg and _bottom.jpg
        """
        self.node = node
        
        # load the 6 textures of the node
        resourcesDir = '/c/Documents and Settings/Fidel/workspace/Panorama/demo/data/nodes/' + self.node.getName()
        
        prefixFilename = os.path.join(resourcesDir, self.node.getName())

        #self.resources.getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, self.node.getName() + '_fr.jpg')                
        
        self.faceTextures[PanoConstants.CBM_FRONT_FACE].read(Filename(prefixFilename + '_fr.jpg'))
        self.faceTextures[PanoConstants.CBM_FRONT_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_FRONT_FACE].setWrapV(Texture.WMClamp)
        
        self.faceTextures[PanoConstants.CBM_BACK_FACE].read(Filename(prefixFilename + '_bk.jpg'))
        self.faceTextures[PanoConstants.CBM_BACK_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_BACK_FACE].setWrapV(Texture.WMClamp)
        
        self.faceTextures[PanoConstants.CBM_LEFT_FACE].read(Filename(prefixFilename + '_lt.jpg'))
        self.faceTextures[PanoConstants.CBM_LEFT_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_LEFT_FACE].setWrapV(Texture.WMClamp)
        
        self.faceTextures[PanoConstants.CBM_RIGHT_FACE].read(Filename(prefixFilename + '_rt.jpg'))
        self.faceTextures[PanoConstants.CBM_RIGHT_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_RIGHT_FACE].setWrapV(Texture.WMClamp)
        
        self.faceTextures[PanoConstants.CBM_TOP_FACE].read(Filename(prefixFilename + '_top.jpg'))
        self.faceTextures[PanoConstants.CBM_TOP_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_TOP_FACE].setWrapV(Texture.WMClamp)
        
        self.faceTextures[PanoConstants.CBM_BOTTOM_FACE].read(Filename(prefixFilename + '_bt.jpg'))
        self.faceTextures[PanoConstants.CBM_BOTTOM_FACE].setWrapU(Texture.WMClamp)
        self.faceTextures[PanoConstants.CBM_BOTTOM_FACE].setWrapV(Texture.WMClamp)
        
    def loadCubeModel(self):   
        """
        Loads the egg file that contains the cube model for displaying the cubic
        panorama. 
        After loading we extract references to the faces' textures in order to alter
        the in-game and we also measure the dimensions of the cubemap after taking into
        account the face dimension as specified in the .egg file, the model scale applied
        by the model creator and finally the scale set on the respective nodepath.
        
        Note: There exists a convention that the name of the cube model must be 'cubemap.egg'.
        
        Note:  There exists a convention regarding the order of the geoms definitions in
        the .egg file. Specifically the cubemap model must list the faces in the following 
        order:   top, left, bottom, right, back, front        
        """
        resourcesDir = '/c/Documents and Settings/Fidel/workspace/Panorama/demo/data/models'
        self.cmap = loader.loadModel(os.path.join(resourcesDir, 'cubemap-5.egg'))
        self.cmap.reparentTo(render)
        self.cmap.setScale(10, 10, 10)
        self.cmap.setPos(0,0,0)
        
        # Disable depth write for the cube map
        self.cmap.setDepthWrite(False)    
        
        #Examine the geoms to extract references to their textures.
        #The cubemap model lists the faces inside the egg file in the following order:
        # top, left, bottom, right, back, front
        print self.cmap.ls()

        self.faceDim = 2.0 * self.cmap.getScale()[0]        
        self.faceHalfDim = self.cmap.getScale()[0]          
                        
        cubeGeoms = {
                     PanoConstants.CBM_TOP_FACE : 'top',
                     PanoConstants.CBM_LEFT_FACE : 'left',
                     PanoConstants.CBM_BOTTOM_FACE : 'bottom',
                     PanoConstants.CBM_RIGHT_FACE : 'right',
                     PanoConstants.CBM_BACK_FACE : 'back',
                     PanoConstants.CBM_FRONT_FACE : 'front',
                     
        }
        for i, n in cubeGeoms.items():
            geomNode = self.cmap.find("**/Cube/=name=" + n)     
            state = geomNode.node().getGeomState(0)
            tex = state.getAttrib(TextureAttrib.getClassType()).getTexture()
            self.faceTextures[i] = tex 
                                    
        facesCoords = {
            PanoConstants.CBM_FRONT_FACE : (-self.faceHalfDim, self.faceHalfDim, self.faceHalfDim, 1, 0, -1),
            PanoConstants.CBM_BACK_FACE : (self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim, -1, 0, -1),
            PanoConstants.CBM_RIGHT_FACE : (self.faceHalfDim, self.faceHalfDim, self.faceHalfDim, 0, -1, -1),
            PanoConstants.CBM_LEFT_FACE : (-self.faceHalfDim, -self.faceHalfDim, self.faceHalfDim, 0, 1, -1),
            PanoConstants.CBM_TOP_FACE : (-self.faceHalfDim, self.faceHalfDim, self.faceHalfDim, 1, -1, 0),
            PanoConstants.CBM_BOTTOM_FACE : (-self.faceHalfDim, self.faceHalfDim, self.faceHalfDim, 1, -1, 0)
        }
        for face, coords in facesCoords.items():            
            matOffset = Mat4()
            matOffset.setTranslateMat(VBase3(-coords[0], -coords[1], -coords[2]))
            matScale = Mat4()
            matScale.setScaleMat(VBase3(coords[3] / self.faceDim, coords[4] / self.faceDim, coords[5] / self.faceDim))
            self.worldToFaceMatrices[face] = matOffset * matScale 
            
    """
    Translates the given world space point in the local 2D coordinate system
    of the specified face. The local space extends in [0..1] in the vertical
    and horizontal axis, thus the method returns a tuple of x, y values in the
    [0..1] range.
    """
    def getFaceLocalCoords(self, face, p):        
#        coords = facesCoords[face]                 
#        lp_x, lp_y, lp_z = (p.getX() + self.faceHalfDim) / self.faceDim, (p.getY() + self.faceHalfDim) / self.faceDim, (p.getZ() + self.faceHalfDim) / self.faceDim
#        if coords[3] < 0: lp_x = 1.0 - lp_x
#        if coords[4] < 0: lp_y = 1.0 - lp_y
#        if coords[5] < 0: lp_z = 1.0 - lp_z
#        print 'lp_x, lp_y, lp_z  ', lp_x, ' ', lp_y, '  ', lp_z
        
#        lp_x, lp_y, lp_z = p.getX() - coords[0], p.getY() - coords[1], p.getZ() - coords[2]
#        lp_x = (coords[3] * lp_x) / self.faceDim
#        lp_y = (coords[4] * lp_y) / self.faceDim
#        lp_z = (coords[5] * lp_z) / self.faceDim
#        
#        print 'old ', lp_x, ' ', lp_y, ' ', lp_z
        
        mat = self.worldToFaceMatrices[face]        
        fp = mat.xformPoint(p)        
        if fp.getX() < 0.00001:
            return (fp.getY(), fp.getZ())
        elif fp.getY() < 0.00001:
            return (fp.getX(), fp.getZ())
        else:
            return (fp.getX(), fp.getY())                
        
#        if coords[3] == 0:    return (lp_y, lp_z)
#        elif coords[4] == 0:    return (lp_x, lp_z)
#        else:    return (lp_x, lp_y)

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
    
    
