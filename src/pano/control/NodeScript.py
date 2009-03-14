'''
Created on 9 Mar 2009

@author: Fidel
'''

import logging

from fsm import FSMState

class BaseNodeScript(FSMState):
    '''
    Contains logic for controlling user interaction within a game node.
    '''


    def __init__(self, game, name):
        FSMState.__init__(self, game, name)
        self.log = logging.getLogger('pano.baseNodeScript')
        
        
        