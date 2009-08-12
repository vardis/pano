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

from pano.resources.MultifileResourcesLocation import MultifileResourcesLocation
from pano.resources.DirectoryResourcesLocation import DirectoryResourcesLocation

class ResourcesLocationsFactory(object):
    '''
    Creates instances of ResourcesLocation based on a symbolic string identifier, i.e. a path, a filename,
    a URL.
    '''
    
    log = logging.getLogger('ResourcesLocationsFactory')
        
        
    def create(locationID, name, resTypes):
        if not type(locationID) == str:
            ResourcesLocationsFactory.log.error('Invalid location identifier, cannot create instance')
        
        if locationID.endswith('.mf'):
            return MultifileResourcesLocation(locationID, name, resTypes)
        elif os.path.exists(locationID):
            return DirectoryResourcesLocation(locationID, name, '', resTypes)
    
    create = staticmethod(create)

         