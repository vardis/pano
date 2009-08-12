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

from pano.constants import PanoConstants

class AbstractResourceLocation(object):
    """
    A location from where resources will be found and loaded.
    This class serves as a base for classes that will implement
    specific types of resource locations like filesystem folders,
    multifiles, archives, databases, network streams, etc.
    """
    def __init__(self, name = '', descrption = '', resTypes = PanoConstants.RES_TYPE_ALL, hotswap = True, checkPeriod = 10):
        self.name = name
        self.desc = descrption

        # specifies which resources types will be looked up in this location
        if type(resTypes) == list or type(resTypes) == tuple:
            self.resTypes = []
            self.resTypes.extend(resTypes)
        else:
            self.resTypes = resTypes

        # indicates if the resources within this resource location should get pre-loaded
        self.preload = False

        # indicates if the resources withing thies resource location should remain
        # loaded during the lifetime of the application
        self.sticky = False

        # if True then the location will be checked for any modified resources
        self.hotswap = hotswap

        # the period at which the location will be checked for any modifications.
        # it is defined in seconds
        self.checkPeriod = checkPeriod

    def getName(self):
        return self.name

    def getDescription(self):
        return self.descrption


    def setDescription(self, descrption):
        self.descrption = descrption


    def getPreload(self):
        return self.preload


    def setPreload(self, value):
        self.preload = value

    def setSticky(self, value):
        self.sticky = value
        
    def isSticky(self):
        return self.sticky

    def getResourcesTypes(self):
        return self.resTypes 

    def indexResources(self):
        """
        Creates an index on the resources' names for fast lookups.
        This is exposed as a public function in order to be possible
        to force a rebuild of the index when we know that something
        has changed.
        """
        pass

    def containsResource(self, filename):
        """
        Returns True if this resource location contains the specified filename.
        """
        return False

    def getResourceFullPath(self, name):
        """
        Temporary until streams are incorporated.
        """
        return None
    
    def listResources(self, resType, fullPaths=True):
        """
        List all filenames of type that matches resType. 
        """
        return []

    def getResourceAsString(self, filename, fullPath = False):
        """
        Returns a string that represents the file's contents. Derived class should implement this function.
        @param filename: The resource filename.
        @param fullPath: Specifies if the filename parameter denotes a full path or a base filename. 
        """    
        return None
    
    def getResourceAsByteArray(self, filename, fullPath = False):
        """
        Returns an array of bytes that represent the file's contents. Derived class should implement this function.
        @param filename: The resource filename.
        @param fullPath: Specifies if the filename parameter denotes a full path or a base filename.
        """
        return None

    def hasChanged(self):
        """
        Returns True if any resources have been modified.
        Derived classes should implement this function in order for hot-swapping
        to work.
        """
        return False

    def dispose(self):
        """
        Since ResourcesLocations objects might consume plenty of resources
        for storing their index or utilising system resources (file handles,
        network sockets, threads) for accessing their data sources, this method
        provides a means for releasing these resources when they are no longer
        needed.
        Derived class should implement this function.
        """
        pass

    
