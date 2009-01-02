import logging

from pandac.PandaModules import VBase3, TextNode, NodePath
from direct.gui.DirectGui import DirectButton, DirectLabel

from constants import PanoConstants

class TalkBox:

    def __init__(self, game, x = 0, y = 0, width = 0, height = 0, text = '', fontName = 'bluebold.ttf', bgColor = VBase3(0.0,0.0,0.0), bgImage = None, fgColor = VBase3(1.0,1.0,1.0)):
        self.log = logging.getLogger('pano.talkbox')
        self.game = game
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__text = text
        self.__fontName = fontName
        self.__backgroundColor = bgColor
        self.__backgroundImage = bgImage
        self.__defaultColor = fgColor
        
        self.__isHidden = True
        self.__font  = None
        self.__talkBoxNode = aspect2d.attachNewNode('talkBox')
        self.__textNodeParent = self.__talkBoxNode.attachNewNode('talkBox_text_parent')

    def getText(self):
        return self.__text


    def setText(self, value):
        self.__text = value
        self.__textNode.setText(value)

    def getX(self):
        return self.__x


    def getY(self):
        return self.__y


    def getWidth(self):
        return self.__width


    def getHeight(self):
        return self.__height


    def getFontName(self):
        return self.__fontName


    def getBackgroundColor(self):
        return self.__backgroundColor


    def getBackgroundImage(self):
        return self.__backgroundImage


    def getDefaultColor(self):
        return self.__defaultColor


    def setX(self, value):
        self.__x = value


    def setY(self, value):
        self.__y = value


    def setWidth(self, value):
        self.__width = value


    def setHeight(self, value):
        self.__height = value


    def setFontName(self, value):
        self.__fontName = value


    def setBackgroundColor(self, value):
        self.__backgroundColor = value


    def setBackgroundImage(self, value):
        self.__backgroundImage = value


    def setDefaultColor(self, value):
        self.__defaultColor = value

    
    def showText(self, text, textColor = None):
        self.setText(text)
        if textColor is not None:
            self.setDefaultColor(textColor)

        if self.__font is None:
            fontPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_FONTS, self.__fontName)
            self.__font = loader.loadFont(fontPath)
                
#        self.__textNodeParent.setScale(0.06)
        
        LB = DirectLabel(parent=self.__textNodeParent, 
                         text='',                          
                         text_bg=(self.__backgroundColor[0], self.__backgroundColor[1], self.__backgroundColor[2], 1.0), 
                         text_align = TextNode.ALeft,                        
                         pos=(base.a2dLeft, 0.1, base.a2dBottom + 0.1), 
                         frameSize=(base.a2dLeft, 2*base.a2dRight, base.a2dBottom, 0.3),
                         frameColor=(0,0,0,1))
        self.log.debug('base.a2dBottom %f', base.a2dBottom)
        
        DB = DirectButton(
         parent=self.__textNodeParent,
         text=text,
         text_fg=(self.__defaultColor[0], self.__defaultColor[1], self.__defaultColor[2], 1.0),
         frameSize=(base.a2dLeft, 2*base.a2dRight, base.a2dBottom, 0.3), 
         frameColor=(0,0,0,0),
         text_wordwrap=50,
         text_align = TextNode.ACenter,
         scale=.06, 
         pos=(0, 0, base.a2dBottom + 0.3), 
         pressEffect=0
         #command=,
         )
        
        # text0 : normal
        # text1 : pressed
        # text2 : rollover
        # text3 : disabled
#        for t in ('text1','text2'):
#            DB._DirectGuiBase__componentInfo[t][0].setColorScale(0.5, 1.0, 0.5, 1)
                
        
#        self.show()
    
    def show(self):
        NodePath(self.__textNode).show()
    
    def hide(self):
        NodePath(self.__textNode).hide()
    
    def isHidden(self):
        return NodePath(self.__textNode).isHidden()

    
    x = property(getX, setX, None, "X's Docstring")

    y = property(getY, setY, None, "Y's Docstring")

    width = property(getWidth, setWidth, None, "Width's Docstring")

    height = property(getHeight, setHeight, None, "Height's Docstring")

    fontName = property(getFontName, setFontName, None, "Font's Docstring")

    backgroundColor = property(getBackgroundColor, setBackgroundColor, None, "BackgroundColor's Docstring")

    backgroundImage = property(getBackgroundImage, setBackgroundImage, None, "BackgroundImage's Docstring")

    defaultColor = property(getDefaultColor, setDefaultColor, None, "DefaultColor's Docstring")        

    text = property(getText, setText, None, "Text's Docstring")
    