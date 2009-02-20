import logging

from constants import PanoConstants 
from fsm import FSMState
from actions.builtinActions import ShowDebugConsoleAction, HideDebugConsoleAction

class ConsoleState(FSMState):
    
    NAME = 'ConsoleState'
    
    def __init__(self, gameRef):
        FSMState.__init__(self, gameRef, ConsoleState.NAME)        
        self.log = logging.getLogger('pano.consoleState')
        
    def enter(self):
        FSMState.enter(self)
        self.log.debug('entered console state')
        self.getGame().getInput().pushMappings('console')
    
    def exit(self):
        FSMState.exit(self)
        self.log.debug('exited console state')
        self.getGame().getInput().popMappings()
    
    def update(self, millis):
        pass
    
#    def onInputAction(self, action):
#        if action == "hide_console":
#            self.getGame().hideDebugConsole()
#        elif action == "acShowConsole":
#            pass
#        else:
#            return False
#        return True
        
        
    
    