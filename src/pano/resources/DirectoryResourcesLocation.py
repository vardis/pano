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

import dircache
import fnmatch
import logging
import os
import codecs

from pano.resources.ResourcesLocation import AbstractResourceLocation
from pano.resources.ResourcesTypes import ResourcesTypes


class DirectoryResourcesLocation(AbstractResourceLocation):
    '''
    Offers services for finding loading files from directories.
    '''
    
    def __init__(self, directory, name, description, resTypes, hotswap=True, checkPeriod=10):
        AbstractResourceLocation.__init__(self, name, description, resTypes, hotswap, checkPeriod)
        
        self.log = logging.getLogger('pano.directoryResource')
        
        # the directory to look into for supported resource types
        self.directory = directory

        # a sorted list of all filenames of supported types that were found in self.directory
        self.resourcesNames = []
        
        
    def dispose(self):
        self.resourcesNames = None
        
        
    def indexResources(self):        
        
        # get a listing of the directory and match filenames against
        # all supported resource types
        try:
            filenames = dircache.listdir(self.directory)
        except Exception, e:
            # dircache.listdir can throw 
            self.log.exception('error while calling dircache.listdir')
            return 
        
        suffixes = []
        for resType in self.resTypes:                     
            suffixes.extend(ResourcesTypes.getExtensions(resType))

        suffixes = tuple(suffixes)
        self.resourcesNames = [item for item in filenames if item.endswith(suffixes)]
        self.resourcesNames.sort()


    def containsResource(self, filename):
        return self.resourcesNames.count(filename) > 0


    def getResourceFullPath(self, name):
        if self.resourcesNames.count(name) > 0:
            return os.path.join(self.directory, name)
        else:
            return None
        
        
    def getResourceAsString(self, filename, fullPath = False):
        """
        Returns a string that represents the file's contents.
        @param filename: The resource filename.
        @param fullPath: Specifies if the filename parameter denotes a full path or a base filename. 
        """        
        resPath = self.getResourceFullPath(filename) if not fullPath else filename
        with codecs.open(resPath, 'r', "utf-8") as fp:
            try:
                return fp.read()                
            except Exception,e:
                self.log.exception(e)        


    def getResourceAsByteArray(self, filename, fullPath = False):
        """
        Returns an array of bytes that represent the file's contents.
        It performs the same functionality with getResourceAsString since the str type is used to 
        store byte arrays but it won't decode the string since it doesn't make sense for binary data.
        @param filename: The resource filename.
        @param fullPath: Specifies if the filename parameter denotes a full path or a base filename.
        """
        resPath = self.getResourceFullPath(filename) if not fullPath else filename
        with open(resPath, 'rb') as fp:
            try:
                return fp.read()                
            except Exception,e:
                self.log.exception(e)
                

    def listResources(self, resType, fullPaths=True):
        if resType in self.getResourcesTypes():
            prefix = ''
            if fullPaths:
                prefix = self.directory
            return [os.path.join(prefix, resName) for resName in self.resourcesNames if ResourcesTypes.isExtensionOfType(resName[-4:], resType)]
        else:
            return []

                
    def __str__(self):
        return 'Resource location %s, at path %s, of type %s' % (self.name, self.directory, self.resTypes)     
                   
