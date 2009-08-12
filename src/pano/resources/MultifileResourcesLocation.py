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
import os
import codecs

from pandac.PandaModules import VirtualFileSystem, Filename
from pandac.PandaModules import DSearchPath

from pano.resources.ResourcesLocation import AbstractResourceLocation
from pano.resources.ResourcesTypes import ResourcesTypes

class MultifileResourcesLocation(AbstractResourceLocation):
    '''
    Offers services for finding loading files from multifiles. 
    '''


    def __init__(self, mfFilename, name, resTypes, hotswap=True, checkPeriod=10):
        
        AbstractResourceLocation.__init__(self, name, '', resTypes, hotswap, checkPeriod)
        
        self.log = logging.getLogger('pano.multifileResources')
        
        # where we are mounted on the virtual filesystem
        self.mountPoint = "/" + os.path.basename(mfFilename)        
        
        # the filename of the multifile
        self.filename = mfFilename

        # a sorted list of all filenames of supported types that were found in self.directory
        self.resourcesNames = []
        
        
    def dispose(self):
        vfs = VirtualFileSystem.getGlobalPtr()
        vfs.unmountPoint(Filename(self.mountPoint))
        
                
    def indexResources(self):        
        vfs = VirtualFileSystem.getGlobalPtr()
        vfs.mount(Filename(self.filename), self.mountPoint, VirtualFileSystem.MFReadOnly)        

        
    def containsResource(self, filename):
        vfs = VirtualFileSystem.getGlobalPtr()
        vfs.chdir(self.mountPoint)
        flag = vfs.exists(Filename(filename))
        vfs.chdir(self.mountPoint)
        return flag


    def getResourceFullPath(self, filename):
        vfs = VirtualFileSystem.getGlobalPtr()
        resFile = Filename(filename)
        if vfs.exists(resFile):
            searchPath = DSearchPath()
            searchPath.appendDirectory(self.mountPoint)
            
            # if the filename was resolved, resFile is updated to include the full path
            if vfs.resolveFilename(resFile, searchPath):                
                return resFile.getFullpath()
            

    def getResourceStream(self, name):
        vfs = VirtualFileSystem.getGlobalPtr()
        istream = vfs.openReadFile(Filename(name))
        return istream
    
    
    def getResourceAsString(self, filename, fullPath = False):
        """
        Returns a string that represents the file's contents.
        @param filename: The resource filename.
        @param fullPath: Specifies if the filename parameter denotes a full path or a base filename. 
        """    
        vfs = VirtualFileSystem.getGlobalPtr()        
        fs = vfs.readFile(Filename(filename), False)
        if fs is not None:
            return codecs.decode(fs, "utf-8")


    def getResourceAsByteArray(self, filename, fullPath = False):
        """
        Returns an array of bytes that represent the file's contents.
        It performs the same functionality with getResourceAsString since the str type is used to 
        store byte arrays but it won't decode the string since it doesn't make sense for binary data.
        @param filename: The resource filename.
        @param fullPath: Specifies if the filename parameter denotes a full path or a base filename.
        """
        vfs = VirtualFileSystem.getGlobalPtr()        
        return vfs.readFile(Filename(filename))


    def _listResourcesImpl(self, parent, resType, fullPaths = True):
        resFiles = []
        directories = []
        
        vfs = VirtualFileSystem.getGlobalPtr()
        filesList = vfs.scanDirectory(parent)
        if filesList is None:
            return directories
        
        for i in xrange(filesList.getNumFiles()):            
            fileEntry = filesList.getFile(i)            
            if fileEntry.isDirectory():
                directories.append(fileEntry.getFilename())
                continue
            
            if ResourcesTypes.isExtensionOfType(fileEntry.getFilename().getExtension(), resType):
                resFiles.append(fileEntry.getFilename().getFullpath() if fullPaths else fileEntry.getFilename().getBasename())
                
        for dir in directories:
            resFiles.extend(self._listResourcesImpl(dir, resType, fullPaths))
            
        return resFiles
               
                
    def listResources(self, resType, fullPaths=True):
        '''
        Returns a list of all resource filenames, of the given type, which are contained in this multifile.
        '''
        vfs = VirtualFileSystem.getGlobalPtr()
        return self._listResourcesImpl(Filename(self.mountPoint), resType, fullPaths) 
                        
                        
    def __str__(self):
        return 'Multifile resource location %s, mounted on %s, of type %s' % (self.name, self.mountPoint, self.resTypes)    
    
        