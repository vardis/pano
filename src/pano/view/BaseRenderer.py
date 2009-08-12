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

from pano.constants import PanoConstants
from pano.view.VideoPlayer import VideoPlayer
from pano.view.sprites import *


class BaseRenderer(object):
    def __init__(self, resources):

        self.log = logging.getLogger('pano.baseRenderer')

        # used for loading resources
        self.resources = resources

        # the game node that we are rendering
        self.node = None

        # the root scenegraph node
        self.sceneRoot = None        
        
        # sprites in format {hotspot_name : (<spriteRenderInterface instance>)}
        self.spritesByHotspot = {}

        # if True then the debug geometries for the hotspots will be drawn
        self.drawHotspots = False


    def initialize(self):        
        self.debugGeomsParent = None

    
    def dispose(self):
        '''
        Disposes any rendering resources, it assumes that this instance won't be used again.
        '''
        self.clearScene()
        if self.sceneRoot is not None:
            self.sceneRoot.removeNode()
        self.sceneRoot = None


    def clearScene(self):
        '''
        Clears the scenegraph effectively removing all nodes from rendering.
        '''
        # remove and destroy debug geometries        
        self.debugGeomsParent.removeNode()
        self.debugGeomsParent = None

        # same for hotspots
        for sri in self.spritesByHotspot.values():        
            sri.remove()
        
        self.spritesByHotspot = {}


    def displayNode(self, node):
        """
        Displays the given node.
        """
        self.node = node


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
        Returns the Camera instance used for rendering this node.
        '''
        pass
    

    def render(self, millis):
        pass


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


    def drawDebugHotspots(self, flag):
        self.drawHotspots = flag
        if flag:
            self.debugGeomsParent.show()
        else:
            self.debugGeomsParent.hide()
            
            
    def renderHotspot(self, hp, sprite = None):
        '''
        Renders the given hotspot using its associated sprite.Details of the rendering technique
        is left for the subclasses.
        @param hp: The hotspot to render.
        @param sprite: If not None it is used for overriding the hotspot's sprite. 
        '''
        pass
    
    
    def renderHotspotDebugGeom(self, hp):
        '''
        Renders a debug geometry for the given hotspot. Details of the nature of this debug geometry
        is defined explicitly in subclasses.
        @param hp: The hotspot for which to render debug geometry.
        '''
        pass       


    def getHotspotSprite(self, hotspot):
        """
        Returns a SpriteRenderInterface which can be used to control the hotspot's sprite.
        
        @param hotspot: The hotspot instance
        @return: A SpriteRenderInterface instance or None.
        """        
        return self.spritesByHotspot.get(hotspot.name)


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


    def raycastHotspots(self):
        pass


    def getFaceTextureDimensions(self, face):
        """
        Returns a tuple containing the width and height of the cubemap textures.
        tuple[0] holds the width while tuple[1] holds the height of the textures.
        """
        pass


    def findFaceFromNormal(self, n):
        pass
    
    
    def getFaceLocalCoords(self, face, point):
        pass

    



