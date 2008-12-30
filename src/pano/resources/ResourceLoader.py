import os

from constants import PanoConstants
from DirectoryResourcesLocation import DirectoryResourcesLocation
from model.Node import Node
from model.MousePointer import MousePointer
from parsers.PointerParser import PointerParser 
from parsers.NodeParser import NodeParser

class ResourceLoader:
    """
    Stores all declared resource paths for the various resource types.
    """
    def __init__(self):       
		# locations of resources indexed by their supported resource types
        self.resLocations = {}		       
        self.parsers = {
                        PanoConstants.RES_TYPE_POINTERS : PointerParser(),
                        PanoConstants.RES_TYPE_NODES    : NodeParser()
        }
        
    def addResourcesLocation(self, resLoc):
		resTypes = resLoc.getResourcesTypes()
		for type in resTypes:
			if self.resLocations.has_key(type):
				locList = self.resLocations[type]
				locList.append(resLoc)
			else:
				self.resLocations[type] = [ resLoc ]

		# prepare it for lookups
		resLoc.indexResources()
            
    def removeResourcesLocation(self, resLoc):
		resTypes = resLoc.getResourcesTypes()
		for type in resTypes:
			if self.resLocations.has_key(type):
				locList = self.resLocations[type]
				locList.remove(resLoc)
            
    def getResourceFullPath(self, resType, filename):                
        if self.resLocations.has_key(resType):
            locations = self.resLocations[resType]
            if locations is not None:
                for loc in locations:
                    if loc.containsResource(filename):
                        return loc.getResourceFullPath(filename)
        return None
    
    def loadNode(self, name):
        node = Node(name=name)
        self.loadGeneric(PanoConstants.RES_TYPE_NODES, node, name + '.node')
        return node
    
    def loadPointer(self, name):
        """
        Loads the pointer specified by the given filename. If the pointer was loaded successfully a model.MousePointer
        instance will be returned, otherwise None.
        """
        pointer = MousePointer()
        pointer.setName(name)
        self.loadGeneric(PanoConstants.RES_TYPE_POINTERS, pointer, name + '.pointer')
        
        return pointer
        
    def loadGeneric(self, resType, resObj, filename):
        assert resType is not None and resType != PanoConstants.RES_TYPE_ALL, 'invalid resource type in loadGeneric'
        resPath = self.getResourceFullPath(resType, filename)
        if resPath is not None:
            istream = None
            try:
                istream = open(resPath, 'r')
                resource = self.parsers[resType].parse(resObj, istream)
                return resource
            finally:
                if istream is not None:
                    istream.close()
        else:
            return None
            
        
           

