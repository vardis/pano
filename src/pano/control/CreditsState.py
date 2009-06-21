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

import logging, sys, string, math 

from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
import direct.directbase.DirectStart
from direct.interval.LerpInterval import LerpPosInterval

from pano.constants import PanoConstants
from pano.control.fsm import FSMState
from pano.util.PandaUtil import PandaUtil

class CreditsState(FSMState):
    '''
    Controls the state of the game while displaying the credits page.
    '''

    def __init__(self, gameRef = None):        
        FSMState.__init__(self, gameRef, PanoConstants.STATE_CREDITS)        
        
        self.log = logging.getLogger('pano.creditsState')
        self.alphaMask = None
        self.tex = None
        
        # scene root
        self.scene = None
        
        # parent node of self.creditsOST
        self.textParent = None 
        
        # filename of the background image
        self.background = None
        
        # OnscreenImage used for background rendering
        self.backgroundOSI = None
        
        # name of the font definition to use
        self.fontName = None
        
        self.fontColor = None
        
        # scroll speed in pixels / s
        self.scrollSpeed = 1.0
        
        # the duration of credits
        self.scrollTime = 0.0
        
        self.credits = None
        
        # OnscreenText object for rendering the credits
        self.creditsOST = None  
        
        # positional interval used to scroll the texts
        self.scrollInterval = None 
        
        self.camera = None
        self.camNP = None
        
        self.displayRegion = None
        
        self.playlist = None
        
    def _configure(self):
        cfg = self.game.getConfig()
        self.background = cfg.get(PanoConstants.CVAR_CREDITS_BACKGROUND)
        self.fontName = cfg.get(PanoConstants.CVAR_CREDITS_FONT)
        self.fontColor = cfg.getVec4(PanoConstants.CVAR_CREDITS_FONT_COLOR)
        self.fontScale = cfg.getFloat(PanoConstants.CVAR_CREDITS_FONT_SCALE)
        self.scrollSpeed = cfg.getFloat(PanoConstants.CVAR_CREDITS_SCROLL_SPEED)  
        self.playlist = cfg.get(PanoConstants.CVAR_CREDITS_MUSIC)
        
        creditsFile = cfg.get(PanoConstants.CVAR_CREDITS_TEXT_FILE)
        self.credits = self.game.getResources().loadText(creditsFile)      
        
    def enter(self):
        
        FSMState.enter(self)
        
        self.game.getView().fadeOut(1.0)
        
        self._configure()
        
        globalClock.setMode(ClockObject.MSlave)                 

        # create alpha mask that fades the top and bottom
        img = PNMImage(8,8)
        img.addAlpha()
        img.fill(1)
        img.alphaFill(1)
        for x in range(img.getXSize()):
            for y in range(img.getYSize()):
                img.setAlpha(x,y,-.2+2.5*math.sin(math.pi*y/img.getYSize()))
        self.alphaMask = img
        
        # create texture for applying the alpha mask
        self.tex = Texture()
        self.tex.load(self.alphaMask)
        self.tex.setWrapU(Texture.WMClamp)
        self.tex.setWrapV(Texture.WMClamp)        
        
        # create scenegraph
        self.scene = NodePath('credits_scene_root')
        self.scene.setDepthTest(False)
        self.scene.setDepthWrite(False)
        
        self.textParent = self.scene.attachNewNode('text_parent')        
        
        ts = TextureStage('')
        self.textParent.setTexGen(ts,TexGenAttrib.MWorldPosition)
        self.textParent.setTexScale(ts,.5,.5)
        self.textParent.setTexOffset(ts,.5,.5)
        self.textParent.setTexture(ts,self.tex)
        
        
        # background
        self.backgroundOSI = OnscreenImage(self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, self.background),
                            parent = render2d) 
        
        #  create credits text
        i18n = self.game.getI18n()        
        localizedFont = i18n.getLocalizedFont(self.fontName)
        fontPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_FONTS, localizedFont)                                    
        fontRes = loader.loadFont(fontPath)
                        
        self.creditsOST = TextNode('creditsTextNode')
        crNP = self.textParent.attachNewNode(self.creditsOST)
        crNP.setScale(self.fontScale*PandaUtil.getFontPixelPerfectScale(fontRes))        
        self.creditsOST.setFont(fontRes)
        self.creditsOST.setEncoding(TextEncoder.EUtf8)
        self.creditsOST.setText(self.credits)
        self.creditsOST.setTextColor(Vec4(self.fontColor[0], self.fontColor[1], self.fontColor[2], self.fontColor[3]))        
        self.creditsOST.setAlign(TextNode.ACenter)
        crNP.setP(-90)
        crNP.flattenLight()        
        
        b3 = self.textParent.getTightBounds()
        dims = b3[1]-b3[0]
        
        pixels = PandaUtil.unitsToPixelsY(dims[1] + 2.0 - 1.05)
        self.scrollTime = pixels / self.scrollSpeed
        self.log.debug('time to scroll: %f' % self.scrollTime)
        self.scrollInterval = LerpPosInterval(self.textParent, self.scrollTime, Point3(0,dims[1]+2,0),Point3(0,-1.05,0))
        
        # render scene through an orthographic camera
        self.camera = Camera('credits_camera')
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.camera.setLens(lens)

        self.camNP = NodePath(self.camera)
        self.camNP.reparentTo(self.scene)
        self.camNP.setP(-90)
        
        self.displayRegion = self.game.getView().getWindow().makeDisplayRegion()
        self.displayRegion.setClearColor(Vec4(0,0,0,1))
        self.displayRegion.setCamera(self.camNP)
        self.displayRegion.setSort(20)      
        
        self.game.getInput().addMappings('credits')
        
        self.game.getView().fadeIn(.5)
        
        self.scrollInterval.start()
        
        globalClock.setMode(ClockObject.MNormal) 
        
        if self.playlist is not None:
            self.game.getMusic().setPlaylist(self.game.getResources().loadPlaylist(self.playlist))
            self.game.getMusic().play()                        
  
    def update(self, millis):                
        
        self.scrollTime -= (millis / 1000.0)
        
        if self.scrollInterval is not None and not self.scrollInterval.isPlaying():
            self.log.debug('starting scroll interval')
            self.scrollInterval.start()
            
        if self.scrollInterval is None or self.scrollTime < 0: #self.scrollInterval.isStopped():
            self.log.debug(self.scrollInterval)
            self.log.debug('stopping scrollInterval')
            self.game.quit()
#            self.game.getState().scheduleStateChange(PanoConstants.STATE_EXIT)
    
    def exit(self):
        
        FSMState.exit(self)
        
        if self.playlist is not None:            
            self.game.getMusic().stop()
        
        self.game.getInput().removeMappings('credits')
        
        if self.displayRegion is not None:
            base.win.removeDisplayRegion(self.displayRegion)
            self.displayRegion = None
            
        self.camera = None
        
        if self.scrollInterval is not None:
            self.scrollInterval.finish()
        self.scrollInterval = None        
        
        self.backgroundOSI.destroy()        
        self.backgroundOSI = None
                
        self.creditsOST = None
        
        self.scene.removeNode()
        self.scene = None        
        
        self.tex = None
        self.alphaMask = None
        
    def onInputAction(self, action):
        if action == "interrupt":
            self.log.debug('credits display interrupted')
            if self.scrollInterval is not None:
                self.scrollInterval.finish()
                self.scrollTime = -1.0
            return True
        else:
            return False
        
    def allowPausing(self):
        return False
    
        
        