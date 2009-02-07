import sys
import logging

from actions.builtinActions import *

class GameActions:
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.actions')
        self.game = game            
        self.actions = { }
        self.registerAction(VoidAction())
        self.registerAction(ExitGameAction())
        self.registerAction(PauseGameAction())
        self.registerAction(ResumeGameAction())
    
    def getAction(self, name):
        return self.actions[name]
    
    def registerAction(self, action):
        self.actions[action.getName()] = action
        
    def unregisterAction(self, name):
        del self.actions[name]
        
    def execute(self, name, *params):
        print 'executing action ' + name
        try:
            act = self.actions[name]
            if act is not None:
                act.execute(self.game)
        except: 
            self.log.exception('unexpected error')
#            print ': ', sys.exc_info()[0]

    def isAction(self, name):
        """
        Returns True if the given name corresponds to a known and registered action.
        """
        return self.actions.has_key(name)
            
    def builtinNames(self):
        return BuiltinActionsNames