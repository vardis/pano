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

from pandac.PandaModules import Texture, NodePath, Camera, DisplayRegion
from pandac.PandaModules import TextureAttrib, CullFaceAttrib
from pandac.PandaModules import GeomVertexReader
from pandac.PandaModules import Vec3
from pandac.PandaModules import OrthographicLens
from pandac.PandaModules import LineSegs
from pandac.PandaModules import Filename
from pandac.PandaModules import CardMaker
from direct.showbase.PythonUtil import *
from pandac.PandaModules import Mat4, VBase3, VBase4

from pano.constants import PanoConstants
from pano.model.Node import Node
from pano.model.Sprite import Sprite
from pano.view.sprites import SpritesEngine
from pano.view.NodeRaycaster import NodeRaycaster


class Node2DRenderer:
    def __init__(self, resources):
        
        self.log = logging.getLogger('pano.render2D')
        
        self.resources = resources
        
        # the Node that is being rendered 
        self.node = None
        
        # the scene's root node
        self.sceneRoot = None
        
        # scene node for the full screen quad that renders the background texture of 2D nodes
        self.bgCard = None        
        
        # bounds in XZ plane, by default we assume the node is parented to render2d
        # the order is left, right, top, bottom
        self.bounds = (-1.0, 1.0, -1.0, 1.0)

        self.spritesByHotspot = {}
        self.debugSprites = {}
        
        # used for detecting the hotspot under a window coordinate
        self.raycaster = None
        
        self.spritesEngine = SpritesEngine()


    def initialize(self):                
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.getCamera().node().setLens(lens)
        
        # creates the root node
        if self.sceneRoot is None:
            self.sceneRoot = render2d.attachNewNode(PanoConstants.NODE2D_ROOT_NODE)
            
        self.raycaster = NodeRaycaster(self)
        self.raycaster.initialize()
        
        self.spritesEngine.initialize(self.resources)
                                                

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


    def clearScene(self):
        '''
        Clears the scenegraph effectively removing all nodes from rendering.
        '''        
        if self.bgCard is not None and not self.bgCard.empty():
            self.bgCard.removeNode()
            
        for spr in self.spritesByHotspot.values():
            spr.remove()
            
        for dbgSpr in self.debugSprites.values():
            dbgSpr.remove()

        self.spritesByHotspot = {}
        self.debugSprites = {}
        

    def displayNode(self, node):
        """
        Displays the given node.
        """        
        if self.node is not None and self.node.getName() == node.getName():
            return
        else:                    
            self.clearScene()
            self.node = node        

        if self.node.parent2d is None or self.node.parent2d == Node.PT_Render2D:
            # when the parent is not explicitly defined, then assume render2d
            self.bounds = (-1.0, 1.0, -1.0, 1.0)
            self.sceneRoot.setScale(1.0, 1.0, 1.0)
            self.sceneRoot.reparentTo(render2d)
        else:
            asp = self.getCamera().getLens().getAspectRatio()
            self.bounds = (-asp, asp, -1.0, 1.0)
            aspectRatio = base.getAspectRatio()
            self.sceneRoot.setScale(1.0 / aspectRatio, 1.0, 1.0)
            self.sceneRoot.reparentTo(aspect2d)

        if self.node.image is not None:
            self._setBackgroundTexture()

        self._createHotspotsGeoms()


    def render(self, millis):
        pass

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
        return base.cam2d        
    

    def _setBackgroundTexture(self):
        '''
        Sets the background texture for 2D nodes.
        It creates a full screen quad that has the corresponding texture applied to it.
        Note: The field node.parent2d specifies if the quad will be parented to render2d or aspect2d.
        '''
        bgTex = self.resources.loadTexture(self.node.image)
        if bgTex is not None:
            cm = CardMaker('node_bg')            
            cm.setFrame(self.bounds[0], self.bounds[1], self.bounds[2], self.bounds[3])
            cm.setHasUvs(True)
            self.bgCard = NodePath(cm.generate())
            self.bgCard.setName('2dnode_image')
            self.bgCard.setTexture(bgTex)
            self.bgCard.reparentTo(self.sceneRoot)
            self.bgCard.setBin("fixed", PanoConstants.RENDER_ORDER_BACKGROUND_IMAGE)
        else:
            self.log.error('Failed to set background texture for node %s.' % self.node.name)


    def _createHotspotsGeoms(self):
        """
        Creates nodes for the pickable geometry (a box) of hotspots and their sprite visuals.
        """        
        for hp in self.node.getHotspots():
            self.renderHotspot(hp)
            self.renderHotspotDebugGeom(hp)


    def renderHotspot(self, hp, spriteOverride = None):
        '''
        Renders the given hotspot using its associated sprite.
        @param hp: The hotspot to render. 
        @param sprite: If not None it is used for overriding the hotspot's sprite.
        '''                
        spriteName = hp.sprite if spriteOverride is None else spriteOverride
        if spriteName is not None:
            sprite = self.resources.loadSprite(spriteName)
            if sprite is None:
                self.log.error('Failed to render sprite %s' % sprite.name)
                return
            
            sri = self.spritesEngine.createSprite(sprite)
            sri.setPos(hp.xo + hp.width/2, 1.0, hp.yo + hp.height/2)
            if not hp.active:
                sri.hide()
                
            self.spritesByHotspot[hp.name] = sri
    
    
    def renderHotspotDebugGeom(self, hp):
        '''
        Renders a debug geometry for the given hotspot. 
        @param hp: The hotspot for which to render debug geometry.
        '''
#        dbgSprite = Sprite('debug_' + hp.name)
#        dbgSprite.eggFile = 'debug_box.egg'
#        dbgSprite.width = hp.width
#        dbgSprite.height = hp.height
#                
#        sri = self.spritesEngine.createSprite(dbgSprite)
#        sri.setPos(hp.xo, 1.0, hp.yo)
#        self.debugSprites[hp.name] = sri
                        
    
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
        spr = self.debugSprites.get(hotspot.name)
        if spr is not None:
            spr.remove()            
            del self.debugSprites[hotspot.name]


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
        for spr in self.debugSprites.values():
            spr.show()
        else:
            spr.hide()        
    
                
    def raycastHotspots(self, x, y):
        '''
        Returns the hotspot(s) under the given window coordinates.
        @param x: The x window coordinate.
        @param y: The y window coordinate.
        @return: A list of Hotspot instances or None. 
        '''         
#        x = 0.2968
#        y = -0.2968
#        print 'x, y: ', x, y       
        screenPoint = sprite2d.getRelativePoint(render2d, Vec3(x, 1.0, y))
        hotspots = []
        x = screenPoint.getX()
        y = screenPoint.getZ()
        print 'x, y: ', x, y
        for hp in self.node.getHotspots():                
            if x >= hp.xo and x <= hp.xe and y >= hp.yo and y <= hp.ye:
                hotspots.append(hp)
        return hotspots
    

    def _getImageDimensions(self):
        tex = self.bgCard.getTexture()
        return (tex.getXSize(), tex.getYSize())

        

