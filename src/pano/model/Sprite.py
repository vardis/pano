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
        self.name = name
        self.eggFile = eggFile
        self.image = None
        self.frameRate = frameRate
        self.width = width
        self.height = height
        self.video = video
        self.audio = audio    


        
        