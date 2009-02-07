import logging

from direct.interval.IntervalGlobal import *

from constants import PanoConstants
from control.fsm import FSMState
from view.camera import CameraMouseControl
from control.PausedState import PausedState

class ExploreState(FSMState):
    
    NAME = 'ExploreState'
    
    def __init__(self, gameRef = None, node = None):        
        FSMState.__init__(self, gameRef, ExploreState.NAME)
        
        self.log = logging.getLogger('pano.exploreState')
        self.activeNode = None
        self.cameraControl = CameraMouseControl(self.getGame())
        
        self.talkBoxSequence = None
        
    def enter(self):
        
        FSMState.enter(self)
        
        self.cameraControl.initialize()
                        
        # enable rotation of camera by mouse
        self.cameraControl.enable()

        game = self.getGame()
        
        initialNode = game.getResources().loadNode('node1')                        
        
        game.getView().displayNode(initialNode)                
        game.getView().mousePointer.setByName('select')

        game.getMusic().play()

        self.activeNode = game.getView().getActiveNode()
        
        game.getInput().addMappings('explore')
        
        game.getView().panoRenderer.drawDebugHotspots(
                game.getConfig().getBool(PanoConstants.CVAR_DEBUG_HOTSPOTS, False))
        
        self.talkBoxSequence = Sequence(
                                        Func(game.getI18n().setLanguage, "en"),
                                        Func(game.getView().getTalkBox().showText, "node1.door.desc", 3.0),
                                        Wait(6.0),
                                        Func(game.getI18n().setLanguage, "gr"),
                                        Func(game.getView().getTalkBox().showText, "node1.door.desc", 3.0),
                                        Wait(6.0)
                                        )
        self.talkBoxSequence.loop()        
    
    def registerMessages(self):
        return (
                PanoConstants.EVENT_GAME_RESUMED, 
                PanoConstants.EVENT_GAME_PAUSED
                )
    
    def doMouseAction(self):
        # returns the face code and image space coordinates of the hit point    
        face, x, y = self.getGame().getView().raycastNodeAtMouse()        
        dim = self.getGame().getView().panoRenderer.getFaceTextureDimensions(face)
        x *= dim[0]
        y *= dim[1]
        
        for h in self.activeNode.getHotspots():
            if h.getFace() == face and x >= h.getXo() and x <= h.getXe() and y >= h.getYo() and y <= h.getYe():
                if self.log.isEnabledFor(logging.DEBUG):                    
                    self.log.debug('Clicked on hotspot %s, (%s)', h.getName(), h.getDescription())
                
                self.getGame().getView().getTalkBox().showText(h.getDescription(), 3.0)                                        
                                
#        print 'face culling test:\n'
#        print 'testing isFaceInFrustum from front: ', self.getGame().getView().panoRenderer.isFaceInFrustum(PanoConstants.CBM_FRONT_FACE)
#        print 'testing isFaceInFrustum from back: ', self.getGame().getView().panoRenderer.isFaceInFrustum(PanoConstants.CBM_BACK_FACE)
#        print 'testing isFaceInFrustum from left: ', self.getGame().getView().panoRenderer.isFaceInFrustum(PanoConstants.CBM_LEFT_FACE)
#        print 'testing isFaceInFrustum from right: ', self.getGame().getView().panoRenderer.isFaceInFrustum(PanoConstants.CBM_RIGHT_FACE)
#        print 'testing isFaceInFrustum from top: ', self.getGame().getView().panoRenderer.isFaceInFrustum(PanoConstants.CBM_TOP_FACE)
#        print 'testing isFaceInFrustum from bottom: ', self.getGame().getView().panoRenderer.isFaceInFrustum(PanoConstants.CBM_BOTTOM_FACE)
    
    def exit(self):     
        
        FSMState.exit(self)
        
        self.getGame().getInput().removeMappings('explore')
        
        self.cameraControl.disable()
        
        if self.talkBoxSequence is not None:
            self.talkBoxSequence.finish()
    
    def update(self, millis):
        if not self.getGame().isPaused():
            self.cameraControl.update(millis)
    
    def onMessage(self, msg, *args):
        if msg == PanoConstants.EVENT_GAME_PAUSED:            
            self.talkBoxSequence.pause()
            self.cameraControl.setIsActive(False)
        elif msg == PanoConstants.EVENT_GAME_RESUMED:
            self.talkBoxSequence.resume()
            self.cameraControl.setIsActive(True)    
            
    def onInputAction(self, action):
        if action == "hide_sprites":
            self.hideSprites()
        elif action == "show_sprites":
            self.showSprites()
        elif action == "reset_anims":
            self.resetAnims()        
        elif action == "acMouseAction":
            self.doMouseAction()
        else:
            return False
        return True
    
    def resetAnims(self):
        for hp in self.activeNode.getHotspots():
            spr = hp.getSprite()            
            ri = self.getGame().getView().panoRenderer.getSpriteRenderInterface(spr)
            if ri is not None:
                self.log.debug('setting frame to 1 for sprite %s' % spr)
                ri.setFrame(0)
                
    def hideSprites(self):
        for hp in self.activeNode.getHotspots():
            spr = hp.getSprite()            
            ri = self.getGame().getView().panoRenderer.getSpriteRenderInterface(spr)
            if ri is not None:
                self.log.debug('hiding sprite %s' % spr)
                ri.hide()
                
    def showSprites(self):
        for hp in self.activeNode.getHotspots():
            spr = hp.getSprite()            
            ri = self.getGame().getView().panoRenderer.getSpriteRenderInterface(spr)
            if ri is not None:
                self.log.debug('showing sprite %s' % spr)
                ri.show()
                