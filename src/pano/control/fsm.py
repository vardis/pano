
class FSMState:
    def __init__(self, gameRef = None, name = ''):
        self.name = name
        self.game = gameRef
        
    def getName(self):
        return self.name

    def getGame(self):
        return self.game
        
    def enter(self):
        pass
    
    def exit(self):
        pass
    
    def update(self, millis):
        pass

class FSM:
    """
    A finite state machine has a set of valid states and can have only
    one active state at each time. Along with the active state, a global 
    state can also be active in order to allow all common states behaviour 
    to be coded in that state and execute at all times.
    A FSM in our context can also accept messages and input actions with
    the aim to dispatch any responsive action to the global and current
    states.
    """
    
    def __init__(self, gameRef = None):        
        self.game = gameRef
        
        # a list of the names of all valid states for this FSM        
        self.states = {}
        
        self.globalState = None
        self.currentState = None
        self.previousState = None 
        
    def getGlobalState(self):
        return self.globalState        
        
    def setGlobalState(self, globalState):
        self.globalState = globalState
                
    def getCurrentState(self):
        return self.currentState
        
    def addValidState(self, state):
        self.states[state.getName()] = state
        
    def removeValidState(self, state):
        del self.states[state.getName()]
        
    def getValidStates(self):
        '''
        Returns a copy of the list of valid states names.
        '''
        return self.states.keys()
    
    def update(self, millis):
        if self.globalState is not None:
            self.globalState.update(millis)
            
        if self.currentState is not None:
            self.currentState.update(millis)
            
    def changeState(self, stateName):
        '''
        Changes the current state to the given state. 
        The new state must be a member of the FSM's set of allowable states
        otherwise the transition will be rejected and False will be returned.
        
        Returns: True if the transition was allowed and False if otherwise.
        '''        
        
        if stateName not in self.states.keys():
            return False
        
        if self.currentState is not None:
            self.currentState.exit()
            
        self.previousState = self.currentState
        self.currentState = self.states[stateName]
        self.currentState.enter()
        return True
        
#    def onMessage(self, msg):
#        pass
#    
#    def onInputAction(self, action):
#        pass
        
    
    