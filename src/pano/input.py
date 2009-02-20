
import logging
import Queue
import math

from direct.showbase import DirectObject

from model.ActionMappings import ActionMappings

class InputActionMappings(DirectObject.DirectObject):
    """
    Receives input events from keyboard and mouse and maps these events to game actions
    according to the currently set action map.
    See model.ActionMappings for more details about defining an action map.
    """
    
    def __init__(self, gameRef):
        self.log = logging.getLogger('pano.inputMap')
        self.game = gameRef
        self.globalMap = None
        self.map = None
        self.mapStack = [] 
        self.eventsQueue = Queue.Queue(50)       
        
    def mapInput(self, inputEventName):
        """
        Maps the given input event to its respective action if such a mapping exists.
        
        Returns: the name of the action that maps to this event.
        """
        act = None
        if self.globalMap is not None:
            act = self.globalMap.mapInputEvent(inputEventName)
                        
        if act is None and self.map is not None:
            act = self.map.mapInputEvent(inputEventName)
        
        return act
    
    def setGlobalMappings(self, actionMap):
        if isinstance(actionMap, ActionMappings): 
            self.globalMap = actionMap
        elif isinstance(actionMap, str):
            self.globalMap = self._getMappings(actionMap)
            
        if self.globalMap is not None:
            self._registerPandaEvents()
        
    def setMappings(self, actionMap):
        """
        Replaces the current mappings with the given action map. The parameter actionMap can be either a string, in which
        case it corresponds to the name of a mapping file or a ActionMappings object that directly specifies the mappings.
        """
        if isinstance(actionMap, ActionMappings): 
            self.map = actionMap
        elif isinstance(actionMap, str):
            self.map = self._getMappings(actionMap)
            
        if self.map is not None:
            self._registerPandaEvents()
            
    def addMappings(self, mappingName):
        """
        Adds to the current map, the mappings defined inside the mapping file with given name.
        """
        m = self._getMappings(mappingName)
        if self.map is not None:
            self.setMappings(self.map.union(m))
        else:
            self.setMappings(m)
            
    def removeMappings(self, mappingName):
        """
        Removes from the current map, the mappings defined inside the mapping file with given name.
        """
        m = self._getMappings(mappingName)
        if self.map is not None:
            self.setMappings(self.map.subtract(m))            
    
    def pushMappings(self, mappingName):
        """    
        Replaces the current map with the mappings defined inside the mapping file with given name.
        The old map is saved and can later be reactivated by a corresponding pop operation.        
        """
        # push original mappings if they are not in stack
        if len(self.mapStack) == 0:
            self.mapStack.append(self.map)
            
        self.mapStack.append(self._getMappings(mappingName))
        self.setMappings(self.mapStack[-1])
    
    def popMappings(self):
        """
        Removes the current map and replaces it with the mappings stored by a previous push operation.
        """
        sz = len(self.mapStack) 
        if sz >= 2:
            self.mapStack.pop()
            self.setMappings(self.mapStack[-1])
        elif sz == 1:
            self.setMappings(self.mapStack.pop())            
    
    def clearGlobalMappings(self):
        """
        Clears the current map and any stack history.
        """
        self.globalMap = None        
        self._registerPandaEvents()
    
    def clearMappings(self):
        """
        Clears the current map and any stack history.
        """
        self.map = None
        self.mapStack = []
        self._registerPandaEvents()
        
    def getEvents(self, maxEvents = 50):
        """
        This method should be called periodically to receive the input events, along with their mapped actions, which occurred 
        since the last call to getEvents.
        
        Returns: a list of tuples of the form (event_name, action_name)
        """
        events = []
        cnt = min(maxEvents, self.eventsQueue.qsize())
        if cnt > 0:            
            for i in xrange(cnt):
                try:
                    e = self.eventsQueue.get_nowait()
                    action = self.mapInput(e)
                    events.append((e, action))
                    self.eventsQueue
                                        
                except Queue.Empty:
                    self.log.error("Called processEvents with an empty queue.")
                    break
            
        return events
        
    
    def _getMappings(self, mappingName):
        """
        Internal method that returns a ActionMappings object given the name of the mappings file.
        """
        return self.game.getResources().loadActionMappings(mappingName)
    
    def _registerPandaEvents(self):
        """
        Internal method that registers self to receive all input event, through Panda3D's event system, for the events
        which have an entry in the current input map. 
        """        
        self.ignoreAll()
            
        if self.globalMap is not None:    
            for e in self.globalMap.getEvents():
                self.accept(e, self._eventHandler, [e])
            
        if self.map is not None:
            for e in self.map.getEvents():
                self.accept(e, self._eventHandler, [e])
            
    def _eventHandler(self, e):
        """
        Internal method that receives all Panda3D's input events and stores them in self.eventsQueue for later retrieval
        by getEvents().
        """
        if not self.eventsQueue.full():
            try:
                self.eventsQueue.put_nowait(e)
            except Queue.Full:
                self.log.error("Event queue is full, failed to put new event.")
        else:
            log.warning("Dropped event %s because event queue was full." % e)
    