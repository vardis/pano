
from resources.i18n import i18n

class ParseException(Exception):
    """
    This type of exception is raised when an error occurs while parsing a resource file.
    Query the details of the error using the methods: e.getParseError() and e.getResourceFile
    """
    def __init__(self, error, resFile, args=()):
        super(ParseException, self).__init__()
        self.__msg = 'error.parse.msg'
        self.__error = error
        self.__resFile = resFile
        self.args = args
    
    def getMsg(self):
        return self.__msg


    def getError(self):
        return self.__error % self.args


    def getResFile(self):
        return self.__resFile

    msg = property(getMsg, None, None, "Msg's Docstring")

    error = property(getError, None, None, "Error's Docstring")

    resFile = property(getResFile, None, None, "ResFile's Docstring")

        
        