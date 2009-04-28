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
        self.enabled = True
        self.globalMap = None
        self.map = None
        self.mapStack = [] 
        self.eventsQueue = Queue.Queue(50)   
        
    def enable(self):
        '''
        Enables the input mapping functionality.
        '''
        self.enabled = True
        
    def disable(self):
        '''
        Disables the input mapping functionality.
        '''
        self.enabled = False    
        
    def mapInput(self, inputEventName):
        """
        Maps the given input event to its respective action if such a mapping exists.
        
        Returns: the name of the action that maps to this event.
        """
        if not self.enabled:
            return None
        
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
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('set global mappings to %s' % self.globalMap)
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
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('set mappings to %s' % self.map)
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
        if self.map is not None:
            self.mapStack.append(self.map)
            
        self.mapStack.append(self._getMappings(mappingName))
        self.setMappings(self.mapStack[-1])
    
    def popMappings(self):
        """
        Removes the current map and replaces it with the mappings stored by a previous push operation.
        """
        self.mapStack.pop()
        if len(self.mapStack) > 0:
            self.setMappings(self.mapStack[-1])
        else:
            self.clearMappings()      
    
    def clearGlobalMappings(self):
        """
        Clears the current map and any stack history.
        """
        if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('cleared global mappings')
        self.globalMap = None        
        self._registerPandaEvents()
    
    def clearMappings(self):
        """
        Clears the current map and any stack history.
        """
        if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('cleared mappings')
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
    