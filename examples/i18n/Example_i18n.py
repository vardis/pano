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

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode

from pano.control.NodeScript import BaseNodeScript

class Example_i18n(BaseNodeScript):
    def __init__(self, game, node):
        BaseNodeScript.__init__(self, game, 'Example_i18n', node)
        self.log = logging.getLogger('Example_i18n')
        
        self.currentLanguage = "en";
        
        self.languageToStr = {
                              'en' : 'English',
                              'gr' : 'Greek',       
                              'ar' : 'Arabic',                       
                              'cn' : 'Traditional Chinese'
                              }
        self.languages = ['en', 'gr', 'ar', 'cn']
        
        self.languageLabel = None
        
        
    def enter(self):
        self.log.debug('Entered in Example_i18n')            
        self._updateLanguageLabel()
        
        self.game.getInput().addMappings('i18n')
        
    
    def update(self, millis):
        pass
    
    
    def exit(self):
        pass
    
    
    def onInputAction(self, action):
        if action == 'next_language':
            idx = self.languages.index(self.currentLanguage)
            idx = (idx + 1) % len(self.languages)
            self.currentLanguage = self.languages[idx]
            self.game.getI18n().setLanguage(self.currentLanguage)
            self._updateLanguageLabel()            
            return True        
            
    
    def _updateLanguageLabel(self):
        if self.languageLabel:
            self.languageLabel.setText(self.languageToStr[self.currentLanguage])
        else:
            self.languageLabel = OnscreenText(text = self.languageToStr[self.currentLanguage],
                                         pos = (base.a2dLeft + 0.1, 0.9),
                                         align = TextNode.ALeft,
                                         scale = 0.07,
                                         fg = (1.0, 1.0, 1.0, 1.0),
                                         shadow = (0.0, 0.0, 0.0, 0.7),
                                         mayChange = True
                                         )
        self.game.getView().getTalkBox().showText('hello.world', 1000)
    