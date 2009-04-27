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


class GameError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
        
class PersistenceError(GameError):
    def __init__(self, msg, context):
        GameError.__init__(self, msg)
        self.context = context
        
    def __str__(self):
        return 'An error has originated from the persistence layer: %s. Context name: %s' % (self.message, self.context.getName())    
    
class SaveGameError(GameError):
    def __init__(self, msg):
        GameError.__init__(self, msg)
        
class LoadGameError(GameError):
    def __init__(self, msg):
        GameError.__init__(self, msg)    
    
class ResourceError(GameError):
    def __init__(self, msg):
        GameError.__init__(self, msg)

class GraphicsError(GameError):
    def __init__(self, msg):
        GameError.__init__(self, msg)

class InputError(GameError):
    def __init__(self, msg):
        GameError.__init__(self, msg)

class SoundError(GameError):
    def __init__(self, msg):
        GameError.__init__(self, msg)

