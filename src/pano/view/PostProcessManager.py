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
import types

from pano.view.ScreenFilter import ScreenFilter
from pano.view.commonFilters import CommonFiltersFactory


class PostProcessManager(object):
    '''
    Manages the registry of installed post process filters.
    '''


    def __init__(self, game):        
        self.log = logging.getLogger('pano.postProcessMgr')
        
        self.game = game
        
        # contains the registered factories keyed by the respective filter name
        self.factories = {}
        
        # contains the ScreenFilter instances keyed by name
        self.filters = {} 
        
    def initialize(self):
        self.registerFilterFactory(CommonFiltersFactory(self.game))
        
    def update(self, millis):
        '''
        Updates the state of all enabled filters.
        '''        
        for f in self.filters.values():
            if f.isEnabled(): f.update(millis)
        
    def registerFilterFactory(self, factory):
        '''
        Registers a factory for constructing ScreenFilter objects given their name.
        All factory implementations must provide the following methods:
         
            def createFilter(self, filterName),
            where filterName is a string that represents the unique name for this effect. 
            It must return a ScreenFilter instance or None if creation of the filter failed.
            
            def getFilterNames(self),
            Returns a list of the supported filter names.
        
            def getName(self),
            Returns the name of this factory
        An example factory can be found at pano.view.commonFilters.CommonFiltersFactory. 
        '''
        
        # the following assertions make sure the createFilter method exists in the factory instance        
        assert hasattr(factory, 'createFilter')
        attr = getattr(factory, 'createFilter')
        assert attr
        assert type(attr) == types.MethodType
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Registering filter factory %s' % factory.getName())
        
        for n in factory.getFilterNames():            
            self.factories[n] = factory
        
    
    def enableFilter(self, filterName):
        '''
        Enables the filter specified by the given name.
        '''        
        if not self.filters.has_key(filterName) and not self.factories.has_key(filterName):
            if self.log.isEnabledFor(logging.ERROR):
                self.log.error('No registered factory for filter %s' % filterName)
            return
                
        scFilter = self.filters.get(filterName)
        if scFilter is None:
            # the filter hasn't been instantiated yet, so create it for the first time here
            scFilter = self.factories[filterName].createFilter(filterName)
            self.filters[filterName] = scFilter
            
        if not scFilter.isEnabled():
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('Enabling filter %s' % filterName)
            scFilter.enable()
            
    
    def disableFilter(self, filterName):
        '''
        Disables the filter specified by the given name.
        '''
        if not self.filters.has_key(filterName) and not self.factories.has_key(filterName):
            if self.log.isEnabledFor(logging.ERROR):
                self.log.error('No registered factory for filter %s' % filterName)
            return
        
        scFilter = self.filters.get(filterName)        
        if scFilter is not None and scFilter.isEnabled():
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('Disabling filter %s' % filterName)
            scFilter.disable()
        
        
        
        
        
        
        
        
        