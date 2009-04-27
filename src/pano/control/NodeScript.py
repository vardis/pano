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

from constants import PanoConstants
from fsm import FSMState

class BaseNodeScript(FSMState):
    '''
    Contains logic for controlling user interaction within a game node.
    '''


    def __init__(self, game, name):
        FSMState.__init__(self, game, name)
        self.log = logging.getLogger('pano.baseNodeScript')
        
#    def enter(self):
#        FSMState.enter(self)
#        
#    def exti(self):
#        FSMState.exit(self)
        
    def registerMessages(self):
        return [PanoConstants.EVENT_HOTSPOT_ACTION, PanoConstants.EVENT_HOTSPOT_LOOKAT]
        
        
        