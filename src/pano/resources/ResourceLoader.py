import os

from constants import PanoConstants
from DirectoryResourcesLocation import DirectoryResourcesLocation
from parsers.PointerParser import PointerParser 

class ResourceLoader:
    """
    Stores all declared resource paths for the various resource types.
    """
    def __init__(self):       
		# locations of resources indexed by their supported resource types
        self.resLocations = {}		       
        self.parsers = {
                        PanoConstants.RES_TYPE_POINTERS : PointerParser()
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
    
    def loadPointer(self, filename):
        """
        Loads the pointer specified by the given filename. If the pointer was loaded successfully a model.MousePointer
        instance will be returned, otherwise None.
        """
        pointer = self.loadGeneric(PanoConstants.RES_TYPE_POINTERS, filename)
        pointer.setName(filename)
        return pointer
        
    def loadGeneric(self, resType, filename):
        assert resType is not None and resType != PanoConstants.RES_TYPE_ALL, 'invalid resource type in loadGeneric'
        resPath = self.getResourceFullPath(resType, filename)
        if resPath is not None:
            istream = None
            try:
                istream = open(resPath, 'r')
                resource = self.parsers[resType].parse(istream)
                return resource
            finally:
                if istream is not None:
                    istream.close()
        else:
            return None
            
        
           

