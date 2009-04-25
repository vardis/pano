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
from messaging import Messenger
from control.StatesFactory import StatesFactory

class FSMState(object):
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
        print 'entered in ' , self.name
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
    
    
    def persistState(self, persistence):
        return None
    
    def restoreState(self, persistence, ctx):
        pass

class FSM(object):
    """
    A finite state machine has a set of valid states and can have only
    one active state at each time. Along with the active state, a global 
    state can also be active in order to allow all common states behaviour 
    to be coded in that state and execute at all times.
    A FSM in our context can also accept messages and input actions with
    the aim to dispatch any responsive action to the global and current
    states.
    """
    
    def __init__(self, name, gameRef = None):
                
        self.log = logging.getLogger('pano.fsm')
        self.name = name
        self.game = gameRef        
        self.factory = StatesFactory(self.game)            
        self.states = {}    # contains all the valid states for this FSM keyed by name        
        self.globalState = None
        self.currentState = None
        self.previousGlobalState = None
        self.previousState = None                
        self.statesStack = []
        self.globalStatesStack = []
        self.scheduledChange = None
        
    def getGlobalState(self):
        return self.globalState                
                    
    def getCurrentState(self):
        return self.currentState
    
    def getPreviousGlobalState(self):
        return self.previousGlobalState
    
    def getPreviousState(self):
        return self.previousState
        
#    def addValidState(self, state):
#        self.states[state.getName()] = state
#        
#    def removeValidState(self, state):
#        del self.states[state.getName()]
        
    def getFactory(self):
        return self.factory
    
#    def getValidStates(self):
#        '''
#        Returns a copy of the list of valid states names.
#        '''
#        return self.states.keys()
    
    def update(self, millis):
        
        if self.scheduledChange is not None:
            t = self.scheduledChange[1] - millis
            if t > 0:
                self.scheduledChange[1] = t
            else:
                stateName = self.scheduledChange[0]
                self.scheduledChange = None
                self.changeState(stateName)                
        
        if self.globalState is not None:
            self.globalState.update(millis)
            
        if self.currentState is not None:
            self.currentState.update(millis)
            
    def scheduleStateChange(self, stateName, delay = 0):
        '''
        Schedules the change to the specified state in the time frame specified by the delay parameter.
        If delay is zero then the change will occur at the next update cycle of the FSM.
        Note: delay is assumed to be in milliseconds.
        '''
        self.scheduledChange = [stateName, delay]
            
    def changeState(self, stateName, pushNew=False, popOld=False):
        '''
        Changes the current state to the given state. 
        The new state must be a member of the FSM's set of allowable states
        otherwise the transition will be rejected and False will be returned.
        
        Returns: True if the transition was allowed and False if otherwise.
        '''        
        
        if not self.factory.isRegistered(stateName):
            return False
        
        # when pushing a different stae, we don't need to call exit on the old
        if self.currentState is not None and not pushNew:
            self.currentState.exit()
            
        self.previousState = self.currentState
        self.currentState = self.factory.create(stateName)
        
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
                
#        if stateName not in self.states.keys():
#            return False
        if not self.factory.isRegistered(stateName):
            return False
        
        if self.globalState is not None:
            self.globalState.exit()
                            
        self.previousGlobalState = self.globalState
        self.globalState = self.factory.create(stateName) # self.states[stateName]
        self.globalState.enter()      
        return True  
    
    def pushState(self, stateName):
        """
        Sets the specified state as the new current state but doesn't exit the previous state.
        The old state is not exited but remains ready to be resumed when popState will be called. 
        """
        self.statesStack.append(self.currentState)
        self.currentState.suspend()  
        self.currentState = self.factory.create(stateName)
        self.currentState.enter()
    
    def popState(self):
        """
        Resumes the previously active state.
        As the previously active state was not exited, there won't be a call to its enter method.
        """
        assert len(self.statesStack) > 0, 'popState called on empty state stack'
        oldState = self.statesStack.pop()        
        self.currentState.exit()
        self.currentState = oldState
        self.currentState.resume()
    
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
            self.log.exception("Unexpected error while responding to input action %s" % action)
            return False
        
    def persistState(self, persistence):
        '''
        Saves the FSM's data into a persistence context.        
        '''
        ctx = persistence.createContext('fsm')
        if self.globalState is not None:
            ctx.addVar('globalState', self.globalState.getName())
            
        if self.previousGlobalState is not None:
            ctx.addVar('previousGlobalState', self.previousGlobalState.getName())
            
        ctx.addVar('currentState', self.currentState.getName())
        stateCtx = self.currentState.persistState(persistence)
        ctx.addVar('state_context_' + self.currentState.getName(), persistence.serializeContext(stateCtx))
        
        if self.previousState is not None:
            ctx.addVar('previousState', self.previousState.getName())
        
        if self.statesStack is not None:
            ctx.addVar('statesStack', [s.getName() for s in self.statesStack])
            
            for state in self.statesStack:
                stateCtx = state.persistState(persistence)
                ctx.addVar('state_context_' + state.getName(), persistence.serializeContext(stateCtx))
            
        if self.globalStatesStack is not None:
            ctx.addVar('globalStatesStack', [s.getName() for s in self.globalStatesStack])
            
            for state in self.globalStatesStack:
                stateCtx = state.persistState(persistence)
                ctx.addVar('state_context_' + state.getName(), persistence.serializeContext(stateCtx))                    
        
        return ctx      
    
    def restoreState(self, persistence, ctx):
        
        self._reset()
        
        if ctx.hasVar('globalState'):
            globalStateName = ctx.getVar('globalState')
            self.globalState = self.factory.create(globalStateName)
            
        if ctx.hasVar('previousGlobalState'):
            previousGlobalStateName = ctx.getVar('previousGlobalState')
            self.previousGlobalState = self.factory.create(previousGlobalStateName)
            
        self.currentState = self.factory.create(ctx.getVar('currentState'))
        stateCtx = persistence.deserializeContext(ctx.getVar('state_context_' + self.currentState.getName()))
        self.currentState.restoreState(persistence, stateCtx)
        self.currentState.enter()
        
        if ctx.hasVar('previousState'):
            self.previousState = self.factory.create(ctx.getVar('previousState'))
            
        if ctx.hasVar('statesStack'):
            self.statesStack = []
            statesStack = ctx.getVar('statesStack')
            for state in statesStack:
                stateObj = self.factory.create(state)
                self.statesStack.append(stateObj)
                stateCtx = persistence.deserializeContext(ctx.getVar('state_context_' + state))
                stateObj.restoreState(persistence, stateCtx)
                
        if ctx.hasVar('globalStatesStack'):
            self.globalStatesStack = []
            globalStatesStack = ctx.getVar('globalStatesStack')
            for state in globalStatesStack:
                stateObj = self.factory.create(state)
                self.globalStatesStack.append(stateObj)
                stateCtx = persistence.deserializeContext(ctx.getVar('state_context_' + state))
                stateObj.restoreState(persistence, stateCtx)
                
    def _reset(self):
        '''
        Resets the state machine by disposing and removing all associated states. Thus the resulting
        fsm will not contain any states.
        '''        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('reseting state machine %s' % self.name)
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('destroying global state')
            
        if self.globalState is not None:
            self.globalState.exit()
            self.globalState = None

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('destroying current state')
        if self.currentState is not None:
            self.currentState.exit()
            self.currentState = None
            
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('destroying states stack')
        for state in self.statesStack:            
            state.exit()
        self.statesStack = []
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('destroying global states stack')
        for state in self.globalStatesStack:
            state.exit()
        self.globalStatesStack = []
            
        
    