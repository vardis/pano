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


class Font:
    
    def __init__(self, fontName):
        self.__name = fontName
        self.__localizations = {}
    
    def getLocalized(self, language):
        if self.localizations.has_key(language):
            return self.localizations[language]
        else:
            return None

    def addLocalization(self, language, fontName):
        self.__localizations[language] = fontName

    def getName(self):
        return self.__name


    def getLocalizations(self):
        return self.__localizations.copy()


    def setName(self, value):
        self.__name = value


    def setLocalizations(self, value):
        self.__localizations = value

    name = property(getName, setName, None, "Name's Docstring")

    localizations = property(getLocalizations, setLocalizations, None, "Localizations's Docstring")
