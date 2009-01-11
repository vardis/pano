
class LangFile(dict):
    
    def __init__(self, name, language = 'en'):
        super(LangFile, self).__init__()
        self.name = name
        self.language = language
    
    def getLanguage(self):
        return self.__language


    def setLanguage(self, value):
        self.__language = value

    
    def getName(self):
        return self.__name


    def setName(self, value):
        self.__name = value
        
    name = property(getName, setName, None, "Name's Docstring")

    language = property(getLanguage, setLanguage, None, "Language's Docstring")
        

    

    

        
        