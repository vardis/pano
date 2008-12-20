from actions.names import BuiltInActionsNames
from actions.VoidAction import VoidAction
from actions.ExitGameAction import ExitGameAction

class GameActions:
    
    def __init__(self, game):
        self.game = game
        self.builtins = BuiltInActionsNames()
        self.actions = { }
        self.registerAction(VoidAction())
        self.registerAction(ExitGameAction())
    
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
            print 'unexpected error: ', sys.exc_info()[0]
            
    def builtinNames(self):
        return self.builtins