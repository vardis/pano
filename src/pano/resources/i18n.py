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

from pano.constants import PanoConstants
from pano.model.LangFile import LangFile

"""
import codecs 
ustr = u'\u03b5\u03bb\u03bb\u0387\u03bd\u03ba\u03b1' 
text.setText(codecs.utf_8_encode(ustr)[0]) 
"""
class i18n:
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.i18n')
        self.game = game
        
        # keyed by language code having a dictionary of LangFiles as values
        # keyed in turned by the name of the language file.
        self.messageBundles = {}
        
        # the name of the message bundle to look in by default for translations
        self.__defaultBundle = None

        self.__language = None
        
        self.supportedLanguages = set([])
        
        self.fonts = []

    def initialize(self):
        self.setLanguage(self.game.getConfig().get(PanoConstants.CVAR_I18N_LANG))
        res = self.game.getResources()
        
        translations = res.loadAllLangFiles()
        
        for t in translations:
            self.supportedLanguages.add(t.getLanguage())
            if not self.messageBundles.has_key(t.getLanguage()):
                self.messageBundles[t.getLanguage()] = {}
                
            self.messageBundles[t.getLanguage()][t.getName()] = t
                
        self.fonts = res.loadAllFonts()        

    def getLanguage(self):
        return self.__language

    def setLanguage(self, langCode):
        self.__language = langCode

    def getDefaultBundle(self):
        return self.__defaultBundle


    def setDefaultBundle(self, value):
        self.__defaultBundle = value


    def translate(self, msgKey, bundle = None):
        if not self.isLanguageSupported(self.getLanguage()):
            return str(msgKey) + " could not be translated"
        
        sourceBundle = bundle
        bundles = self.messageBundles[self.getLanguage()]
                
        if sourceBundle is None:
            sourceBundle = self.defaultBundle
            
        if sourceBundle is None:
            for b in bundles.values():                
                if b.has_key(msgKey):
                    return b[msgKey]
        else: 
            b = bundles[sourceBundle]            
            if b.has_key(msgKey):
                return b[msgKey]
        
        return str(msgKey) + " could not be translated"
    
    def getLocalizedFont(self, fontName, language = None):
        lang = language
        if lang is None:
            lang = self.getLanguage()
        assert lang is not None, 'The language is not set!'
                    
        for fnt in self.fonts:
            if fnt.getName() == fontName:
                return fnt.getLocalized(lang)
            
        self.log.error('Could not find a localized version for font %s and language %s', fontName, lang)
        return None
    
    def isLanguageSupported(self, lang):        
        return lang in self.supportedLanguages
    
    def persistState(self, persistence):
        '''
        Saves any internationalisation options into a persistence context.        
        '''
        ctx = persistence.createContext('i18n')
        ctx.addVar('defaultBundle', self.defaultBundle)
        ctx.addVar('language', self.language)
        return ctx
    
    def restoreState(self, persistence, ctx):
        pass

    language = property(getLanguage, setLanguage, None, "The current language of the game")

    defaultBundle = property(getDefaultBundle, setDefaultBundle, None, "DefaultBundle's Docstring")
    

