
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
