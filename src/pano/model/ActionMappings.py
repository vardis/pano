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


class ActionMappings:
    """
    Stores the mappings of the input events to game specific actions.
    """
    
    def __init__(self, name, _mappings = {}):        
        self.name = name
        self.mappings = _mappings # keys are the event names and values the action names
    
    def getName(self):
        return self.name
    
    def addMapping(self, eventName, actionName):
        """
        Adds the mapping for the given event name and action.
        """
        self.mappings[eventName] = actionName
    
    def removeMapping(self, eventName):
        """
        Removes the mapping for the given event name and action.
        """
        del self.mappings[eventName]
    
    def mapInputEvent(self, eventName):
        """
        Maps the given event name to a game action.
        
        Returns: the name of the action
        """
        return self.mappings.get(eventName)
    
    def mapAction(self, actionName):
        """
        Returns a list of input event names that map to the given action name.
        """
        events = []
        for k, v in self.mappings.items():
            if v == actionName:
                events.append(k)
        return events
                
    def union(self, other):
        """
        Returns a new ActionMappings object that contains the mappings of both self and other.
        """
        newMap = self.mappings.copy()                        
        for k, v in other.mappings.items():
            newMap[k] = v
        return ActionMappings(self.name, newMap)
            
    def subtract(self, other):
        """
        Returns a new ActionMappings object that contains the mappings contained in self but not in other.
        """
        newMap = self.mappings.copy()
        for k in other.mappings.keys():
            if newMap.has_key(k):
                del newMap[k]
                
        return ActionMappings(self.name, newMap) 
                
    def getEvents(self):
        """
        Returns a list of all input event names for which a mapping exists.
        """
        return self.mappings.keys()
    
    def getActions(self):
        """
        Returns a list of all game action names for which a mapping exists.
        """
        return self.mappings.values()
    
    