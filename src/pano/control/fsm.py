
import logging 

from constants import PanoConstants
from messaging import Messenger

class FSMState:
    def __init__(self, gameRef = None, name = ''):
        self.log = logging.getLogger('pano.fsm_state')
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
    
    def suspend(self):
        """
        Called when the state is about to get suspended in order to disable any functionalities.        
        """
        pass
    
    def resume(self):
        """
        Called when the state should resume from where it was suspended.
        """
        pass
    
    def registerMessages(self):
        """
        Returns a list of event names that this FSMState instance is interested in receiving.
        A subscription will then be done for these messages.
        """ 
        return []

    def onMessage(self, msg, *args):
        """
        if msg === PanoConstants.EVENT_GAME_PAUSED: ....
        """
        pass
    
    def onInputAction(self, action):
        """
        Called when an input action occurs and this state is the current or global state in a FSM.
        
        Returns: True if the action was handled or False if the action was ignored.
        """        
        return False
    
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
                
        self.log = logging.getLogger('pano.fsm')
        self.game = gameRef                    
        self.states = {}    # a list of the names of all valid states for this FSM        
        self.globalState = None
        self.currentState = None
        self.previousGlobalState = None
        self.previousState = None                
        self.statesStack = []
        self.globalStatesStack = []
        
    def getGlobalState(self):
        return self.globalState                
                    
    def getCurrentState(self):
        return self.currentState
    
    def getPreviousGlobalState(self):
        return self.previousGlobalState
    
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
            
    def changeState(self, stateName, pushNew=False, popOld=False):
        '''
        Changes the current state to the given state. 
        The new state must be a member of the FSM's set of allowable states
        otherwise the transition will be rejected and False will be returned.
        
        Returns: True if the transition was allowed and False if otherwise.
        '''        
        
        if stateName not in self.states.keys():
            return False
        
        # when pushing a different stae, we don't need to call exit on the old
        if self.currentState is not None and not pushNew:
            self.currentState.exit()
            
        self.previousState = self.currentState
        self.currentState = self.states[stateName]
        
        # when poping an old state, we don't need to call enter again on it
        if not popOld:
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
            self.previousGlobalState = self.globalState
            self.globalState = None
            return True
                
        if stateName not in self.states.keys():
            return False
        
        if self.globalState is not None:
            self.globalState.exit()
                            
        self.previousGlobalState = self.globalState
        self.globalState = self.states[stateName]
        self.globalState.enter()      
        return True  
    
    def pushState(self, stateName):
        """
        Sets the specified state as the new current state but doesn't exit the previous state.
        The old state is not exited but remains ready to be resumed when popState will be called. 
        """
        self.statesStack.append(self.currentState.NAME)
        self.changeState(stateName, True, False)
    
    def popState(self):
        """
        Resumes the previously active state.
        As the previously active state was not exited, there won't be a call to its enter method.
        """
        assert len(self.statesStack) > 0, 'popState called on empty state stack'
        self.changeState(self.statesStack.pop(), False, True)
    
    def revertState(self,):
        """
        Returns to the previously active state.
        """
        self.changeState(self.previousState)
        
    
    def allowPausing(self):
        if self.currentState is not None:
            return self.currentState.allowPausing()
        else:
            return True    
    
    def onInputAction(self, action):
        try:
            return (self.globalState and self.globalState.onInputAction(action)) or (self.currentState and self.currentState.onInputAction(action))            
        except:
            self.log.exception("Unexpected error while respoding to input action %s" % action)
            return False
        
    
    