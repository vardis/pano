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

from pandac.PandaModules import VBase3, TextNode, NodePath
from direct.gui.DirectGui import DirectButton, DirectLabel

from constants import PanoConstants

class TalkBox:    
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.talkbox')
        self.game = game
        
        self.timeout = None
        self.accumTime = 0.0
        
        self.activeSound = None     # the sound we play due to a call to self.say
        
        # the font resource
        self.__font = None
        
        # a directlabel that renders the background for the text
        self.__bgLabel = None
        
        # a directbutton that renders the actual text
        self.__textLabel = None                

    def initialize(self):
        self.__talkBoxNode = aspect2d.attachNewNode('talkBox')
        self.__textNodeParent = self.__talkBoxNode.attachNewNode('talkBox_text_parent')
        
        self.setFontName(self.game.getConfig().get(PanoConstants.CVAR_TALKBOX_FONT))
        self.setBackgroundColor(self.game.getConfig().getVec4(PanoConstants.CVAR_TALKBOX_BGCOLOR))
        self.setBackgroundImage(self.game.getConfig().getVec4(PanoConstants.CVAR_TALKBOX_IMAGE))
        self.setTextColor(self.game.getConfig().getVec4(PanoConstants.CVAR_TALKBOX_TEXTCOLOR))
        self.setTextScale(self.game.getConfig().getFloat(PanoConstants.CVAR_TALKBOX_TEXTSCALE))
        
    def update(self, millis):
        if self.timeout is not None:        
            self.accumTime += millis
            if (self.timeout - self.accumTime) <= 0:
                self.timeout = None
                self.accumTime = 0.0                
                self.hide()
                
        if self.activeSound is not None and not self.activeSound.isPlaying():
            self.activeSound.stop()
            self.activeSound = None
            
                
    def say(self, soundName):
        """
        Given the name of a high level sound resource (i.e. a .snd filename without the extension) it will play
        the sound and display its subtitles for the duration of the sound.
        """
        snd = self.game.getResources().loadSound(soundName)
        if snd is not None:
            self.activeSound = self.game.getSoundsFx().playSound(soundName)            
            self.showText(snd.getSubtitles(), self.activeSound.getLength())
        else:
            self.log.error('Could not find sound named: %s' % soundName)
            
    def interrupt(self):
        """
        Interrupts the last say or showText operations by stopping the sound and hiding the text. 
        """
        if self.activeSound is not None:
            self.activeSound.stop()
            self.activeSound = None
            
        self.timeout = None
        self.hide()
        
    def showText(self, text, timeout=None, textColor = None):
        
        #copy text
        self.setText(text)
        
        if textColor is not None:
            self.setTextColor(textColor)
            
        # get localized version of font
        i18n = self.game.getI18n()        
        localizedFont = i18n.getLocalizedFont(self.__fontName)
        fontPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_FONTS, localizedFont)                                    
        self.__font = loader.loadFont(fontPath)
        
        if self.__font:            
            # translate from message key
            translatedText = i18n.translate(text)
            
            # assume a maximum of 10 points per screen unit
            numLines = translatedText.count('\n') + 1
            linesHeight = numLines * self.__textScale * self.__font.getLineHeight()
    
            if self.__bgLabel is not None:
                self.__bgLabel.destroy()
                self.__bgLabel = None
                
            self.__bgLabel = DirectLabel(parent=self.__textNodeParent, 
                             text='',                          
                             text_bg=(self.__backgroundColor[0], self.__backgroundColor[1], self.__backgroundColor[2], self.__backgroundColor[3]), 
    #                         text_align = TextNode.ALeft,                        
                             pos=(base.a2dLeft, 0.1, base.a2dBottom + linesHeight), 
                             frameSize=(base.a2dLeft, 2*base.a2dRight, base.a2dBottom, 1.1*linesHeight),
                             frameColor=(0,0,0,1))
            
            if self.__textLabel is not None:
                self.__textLabel.destroy()
                self.__textLabel = None
                
            self.__textLabel = DirectButton(
             parent=self.__textNodeParent,
             text=translatedText, 
             text_font=self.__font,
             text_fg=(self.__textColor[0], self.__textColor[1], self.__textColor[2], self.__textColor[3]),
             frameSize=(base.a2dLeft, 2*base.a2dRight, base.a2dBottom + 1, linesHeight), 
             frameColor=(0,0,0,0),
             text_wordwrap=None,
             text_align = TextNode.ACenter,
             scale=self.__textScale, 
             pos=(0, 0, base.a2dBottom + linesHeight), 
             pressEffect=0
             )
            
            # text0 : normal
            # text1 : pressed
            # text2 : rollover
            # text3 : disabled
    #        for t in ('text1','text2'):
    #            DB._DirectGuiBase__componentInfo[t][0].setColorScale(0.5, 1.0, 0.5, 1)
                            
            self.timeout = timeout * 1000.0
            self.show()
    
    def show(self):
        self.__talkBoxNode.show()
    
    def hide(self):
        self.__talkBoxNode.hide()
    
    def isHidden(self):
        return self.__talkBoxNode.isHidden()

    def getTextScale(self):
        return self.__textScale


    def setTextScale(self, value):
        self.__textScale = value


    def getText(self):
        return self.__text


    def setText(self, value):
        self.__text = value        

    def getFontName(self):
        return self.__fontName


    def getBackgroundColor(self):
        return self.__backgroundColor


    def getBackgroundImage(self):
        return self.__backgroundImage


    def getTextColor(self):
        return self.__textColor

    def setFontName(self, value):
        self.__fontName = value


    def setBackgroundColor(self, value):
        self.__backgroundColor = value


    def setBackgroundImage(self, value):
        self.__backgroundImage = value


    def setTextColor(self, value):
        self.__textColor = value        

    
    fontName = property(getFontName, setFontName, None, "Font's Docstring")

    backgroundColor = property(getBackgroundColor, setBackgroundColor, None, "BackgroundColor's Docstring")

    backgroundImage = property(getBackgroundImage, setBackgroundImage, None, "BackgroundImage's Docstring")

    textColor = property(getTextColor, setTextColor, None, "TextColor's Docstring")        

    text = property(getText, setText, None, "Text's Docstring")

    textScale = property(getTextScale, setTextScale, None, "TextScale's Docstring")
    