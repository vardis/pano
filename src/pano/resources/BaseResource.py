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

from pandac.PandaModules import NodePath
from pandac.PandaModules import OnscreenImage

class BaseResource(object):
    '''
    Base class for all resource types.
    '''


    def __init__(self, name, data, location):
        
        self.log = logging.getLogger('pano.BaseResource')
        
        # every resource must have a name
        self.name = name
        
        # the related Panda resource 
        self.data = data

        # the name of the resource location containing this resource
        self.location = None
        
        # indicates if this resources has been requested by the user
        self.isRequested = False
        
        # indicates if this resources has been marked to be pre-loaded
        self.preload = False
            
        # indicates that this resources should be kept until the application exits
        self.sticky = False


    def isSticky(self):
        '''
        Returns True if the resource is sticky, i.e. remains in memory for the lifetime of the game
        '''
        return self.sticky


    def setSticky(self, value):
        '''
        Sets the stickiness flag.
        '''
        self.sticky = value
        

    def getPreload(self):
        return self.preload


    def dispose(self, force = False):
        '''
        Releases system resources (textures, models, fonts, buffers, etc.) reserved for this resource.
        '''
        if self.preload and not self.isRequested and not Force:            
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug("won't dispose resource %s because it is marked for preload and hasn't been requested yet." % self.name)
                return
            
        if self.keep and not force:
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug("won't dispose resource %s because it is marked for keeping." % self.name)
                return
                
        if self.data is not None:
            if type(self.data) == NodePath:
                self.data.removeNode()
            elif type(self.data) == OnscreenImage:
                self.data.destroy()
            else:
                # let data get garbage collected
                self.data = None
        
            
        
        
        