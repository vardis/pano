
class ActionMappings:
    """
    Stores the mappings of the input events to game specific actions.
    """
    
    def __init__(self):
        # keys are the event names and values the action names
        self.mappings = {}
    
    def __init__(self, mappings):
        """
        Initialises given the dictionary of mappings.
        """
        self.mappings = mappings
    
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
        return ActionMappings(newMap)
            
    def subtract(self, other):
        """
        Returns a new ActionMappings object that contains the mappings contained in self but not in other.
        """
        newMap = self.mappings.copy()
        for k in other.mappings.keys():
            if newMap.has_key(k):
                del newMap[k]
                
        return ActionMappings(newMap) 
                
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
    
    