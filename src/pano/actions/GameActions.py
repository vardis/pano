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


import sys
import logging

from actions import builtinActions 

class GameActions:
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.actions')
        self.game = game            
        self.actions = { }
        builtinActions.registerBultins(self)
    
    def getAction(self, name):
        return self.actions[name]
    
    def registerAction(self, action):
        self.actions[action.getName()] = action
        
    def unregisterAction(self, name):
        del self.actions[name]
        
    def execute(self, name, *params):
        self.log.debug('executing action %s' % name)
        try:
            act = self.actions[name]
            if act is not None:
                act.execute(self.game)
        except: 
            self.log.exception('unexpected error')

    def isAction(self, name):
        """
        Returns True if the given name corresponds to a known and registered action.
        """
        return self.actions.has_key(name)
            
    def builtinNames(self):
        return builtinActions.BuiltinActionsNames