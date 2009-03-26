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

        
        