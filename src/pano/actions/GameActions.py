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