import logging

from direct.showbase import DirectObject
from pandac.PandaModules import TextNode
from direct.gui.OnscreenText import OnscreenText

from constants import PanoConstants
from control.fsm import FSMState

class PausedState(FSMState, DirectObject.DirectObject):
    
    NAME = 'PausedState'
    
    def __init__(self, gameRef = None):        
        FSMState.__init__(self, gameRef, PausedState.NAME)        
        self.log = logging.getLogger('pano.pausedState')
        
        self.msgKey = "Game Paused"
        self.translatedText = ""
        self.fontName = None
        self.fgColor = None
        self.scale = 1.0
        
        self.mousePointerTask = None
        self.musicTask = None
        self.wasMusicPlaying = False
        
        self.textParent = None
        self.textNode = None
        
    def enter(self):
        
        FSMState.enter(self)
        
        # for testing pausing
        self.accept('p', self.togglePause)
        
        self.getGame().getInput().pushMappings('paused')
        
        # read config
        config = self.game.getConfig() 
        self.msgKey = config.get(PanoConstants.CVAR_PAUSED_STATE_MESSAGE)
        self.fontName = config.get(PanoConstants.CVAR_PAUSED_STATE_FONT)
        self.fgColor = config.getVec4(PanoConstants.CVAR_PAUSED_STATE_FGCOLOR)
        self.scale = config.getFloat(PanoConstants.CVAR_PAUSED_STATE_SCALE)
        
        # translate message and font 
        i18n = self.game.getI18n()
                
        localizedFont = i18n.getLocalizedFont(self.fontName)
        fontPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_FONTS, localizedFont)
        # if font is None, then Panda3D will use a default built-in font                                    
        font = loader.loadFont(fontPath)
        
        self.translatedText = i18n.translate(self.msgKey)
                                              
        self.getMessenger().sendMessage(PanoConstants.EVENT_GAME_PAUSED)
        
        music = self.getGame().getMusic()
        self.wasMusicPlaying = not(music.isPaused() or music.isStopped())
        music.setPaused(True)
        
        self.getGame().getView().panoRenderer.pauseAnimations()
        
        self.getGame().getView().mousePointer.hide()
        
        if self.textParent == None:
            self.textParent = aspect2d.attachNewNode("pausedText")
            
        if self.textNode == None:
            self.textNode = OnscreenText(
                                         text=self.translatedText, 
                                         pos=(0.0, 0.0), 
                                         scale=self.scale, 
                                         fg=self.fgColor,
                                         align=TextNode.ACenter,
                                         font=font,
                                         parent=self.textParent,
                                         mayChange=False)
            
        self.textParent.show()
                                        
    
    def exit(self):
        
        FSMState.exit(self)
        
        self.textParent.hide()
        
        self.getMessenger().sendMessage(PanoConstants.EVENT_GAME_RESUMED)                                
        
        self.getGame().getInput().popMappings()
        
        self.getGame().getView().panoRenderer.resumeAnimations()
        self.getGame().getView().mousePointer.show()        
            
        if self.wasMusicPlaying:
            self.getGame().getMusic().setPaused(False)
    
    def update(self, millis):
        pass
    
    def togglePause(self):
        if not(self.getGame().isPaused()):
            self.getGame().getState().changeGlobalState(None)
            
                        