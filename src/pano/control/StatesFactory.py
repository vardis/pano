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

class StatesFactory(object):
    '''
    Creates FSMState objects given their respective unique names.
    
    You can register new types of states using factory.registerState('myName', MyStateClassName)
    and later create instances using the code: factory.create('myName').
    '''


    def __init__(self, game):
        '''
        Constructor
        '''
        self.log = logging.getLogger('pano.statesFactory')
        self.game = game
        self.states = {}
        
    def registerState(self, name, clazz):
        '''
        Registers a new FSMState type which will be identified in the future by the given name.
        The name should be unique for each class.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('registering state %s for class %s' % (name, clazz))
        self.states[name] = clazz
        
    def isRegistered(self, name):
        return name in self.states.keys()
    
    def create(self, name):
        '''
        Creates and returns an instance of an FSMState type which is identified by the specified unique name.
        It returns None if the given name hasn't been registered.
        '''
        if self.states.has_key(name):
            clazz = self.states[name]
            return clazz(self.game)
        else:
            return None
    
        