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


class Sprite:
    """
    A sprite represents a sequence of images of specified dimensions (width, height).
    The source of the images can be simple images or a video file with audio (optional).
    """
    def __init__(self, name, eggFile=None, frameRate=0, width=0, height=0, video=None, audio=None):
        self.__name = name
        self.__eggFile = eggFile
        self.image = None
        self.__frameRate = frameRate
        self.__width = width
        self.__height = height
        self.__video = video
        self.__audio = audio    

    def getName(self):
        return self.__name


    def setName(self, value):
        self.__name = value


    def getEggFile(self):
        return self.__eggFile


    def getFrameRate(self):
        return self.__frameRate


    def getWidth(self):
        return self.__width


    def getHeight(self):
        return self.__height


    def getVideo(self):
        return self.__video


    def getAudio(self):
        return self.__audio


    def setEggFile(self, value):
        self.__eggFile = value


    def setFrameRate(self, value):
        self.__frameRate = value


    def setWidth(self, value):
        self.__width = value


    def setHeight(self, value):
        self.__height = value


    def setVideo(self, value):
        self.__video = value


    def setAudio(self, value):
        self.__audio = value

    def getImage(self):
        return self.image
    
    def setImage(self, image):
        self.image = image
        
    eggFile = property(getEggFile, setEggFile, None, "EggFile's Docstring")

    frameRate = property(getFrameRate, setFrameRate, None, "FrameRate's Docstring")

    width = property(getWidth, setWidth, None, "Width's Docstring")

    height = property(getHeight, setHeight, None, "Height's Docstring")

    video = property(getVideo, setVideo, None, "Video's Docstring")

    audio = property(getAudio, setAudio, None, "Audio's Docstring")

    name = property(getName, setName, None, "Name's Docstring")
    
        
        