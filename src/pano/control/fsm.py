
from constants import PanoConstants
from messaging import Messenger

class FSMState:
    def __init__(self, gameRef = None, name = ''):
        self.name = name
        self.game = gameRef     
        self.msn = Messenger(self)   
        
    def getName(self):
        return self.name
    
    def getGame(self):
        return self.game    
    
    def getMessenger(self):
        return self.msn
                
    def enter(self):
        self.msn.acceptMessage(PanoConstants.EVENT_GAME_EXIT, self.onMessage)
        self.msn.acceptMessage(PanoConstants.EVENT_GAME_PAUSED, self.onMessage)
        self.msn.acceptMessage(PanoConstants.EVENT_GAME_RESUMED, self.onMessage)
        
        msgList = self.registerMessages()
        if msgList is not None:
            for msg in msgList:
                self.msn.acceptMessage(msg, self.onMessage)
    
    def exit(self):
        self.msn.rejectAll()
    
    def update(self, millis):
        pass
    
    def registerMessages(self):
        return None

    def onMessage(self, msg, *args):
        """
        if msg === PanoConstants.EVENT_GAME_PAUSED: ....
        """
        pass
    
    def allowPausing(self):
        return True

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
        
                    
    def getCurrentState(self):
        return self.currentState
    
    def getPreviousState(self):
        return self.previousState
        
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
        
    def changeGlobalState(self, stateName):
        '''
        Changes the current global state to the given state. 
        The new state must be a member of the FSM's set of allowable states
        otherwise the transition will be rejected and False will be returned.
        
        Returns: True if the transition was allowed and False if otherwise.
        '''
        # users are able to disable the global state since it is not necessary to have one
        if stateName is None:
            if self.globalState is not None:
                self.globalState.exit()
            self.globalState = None
            return True
                
        if stateName not in self.states.keys():
            return False
        
        if self.globalState is not None:
            self.globalState.exit()
                    
        self.globalState = self.states[stateName]
        self.globalState.enter()        
    
    def allowPausing(self):
        if self.currentState is not None:
            return self.currentState.allowPausing()
        else:
            return True
        
    
#    
#    def onInputAction(self, action):
#        pass
        
    
    