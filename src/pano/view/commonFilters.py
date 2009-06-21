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


from ScreenFilter import ScreenFilter


class CommonFiltersFactory(object):
    '''
    Provides instances of the common filters.
    '''
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.CommonsFilters')
        self.game = game
        self.filters = {
                        "BlackAndWhite" : BlackAndWhiteFilter(game),
                        "Heat" : HeatFilter(game),
                        "OldTV" : OldTvFilter(game),
                        "OldMovie" : OldMovieFilter(game),
                        "Negative" : NegativeFilter(game)
                        }        


    def getName(self):
        return 'Common filters factory'
    
    
    def createFilter(self, filterName):
        '''
        Creates the screen filter that is uniquely identified by the given by the given name.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('Creating filter %s' % filterName)

        if self.filters.has_key(filterName):
            return self.filters[filterName]
        else:
            if self.log.isEnabledFor(logging.WARNING):
                self.log.warning('Cannot create unknown filter %s' % filterName)

                
    def getFilterNames(self):
        return self.filters.keys()


class BlackAndWhiteFilter(ScreenFilter):
    def __init__(self, game):
        ScreenFilter.__init__(self, 'BlackAndWhite', game)
        self.setShader('gray')        


class HeatFilter(ScreenFilter):
    def __init__(self, game):
        ScreenFilter.__init__(self, 'Heat', game)
        
        self.setShader('heat')        
        
        self.setTextureParameter('heat', 'HeatLookup.tga')
        self.setTextureParameter('Rand', 'Random3D.dds')
        
        self.setTimeMode(ScreenFilter.Time_0_X)
        self.setPredefinedParameter('time', ScreenFilter.Time)
        
        self.setFloatParameter('interference', (0.21, 0.0, 0.0, 0.0))
        
        
class OldTvFilter(ScreenFilter):
    def __init__(self, game):
        ScreenFilter.__init__(self, 'OldTV', game)
        
        self.setShader('oldTV')        
        
        self.setTextureParameter('Noise', 'NoiseVolume.dds')
        self.setTextureParameter('Rand', 'Random3D.dds')
        
        self.setTimeMode(ScreenFilter.Time_0_X)
        self.setPredefinedParameter('time', ScreenFilter.Time)
        self.setPredefinedParameter('sinTime', ScreenFilter.Sin_Time_0_X)
        
        self.setFloatParameter('interference', (0.21, 0.0, 0.0, 0.0))
        self.setFloatParameter('frameSharpness', (8.4, 0.0, 0.0, 0.0))
        self.setFloatParameter('frameShape', (0.34, 0.0, 0.0, 0.0))
        self.setFloatParameter('frameLimit', (0.38, 0.0, 0.0, 0.0))
        self.setFloatParameter('distortionFreq', (5.7, 0.0, 0.0, 0.0))
        self.setFloatParameter('distortionRoll', (0.4, 0.0, 0.0, 0.0))
        self.setFloatParameter('distortionScale', (6.0, 0.0, 0.0, 0.0))


class OldMovieFilter(ScreenFilter):
    def __init__(self, game):
        ScreenFilter.__init__(self, 'OldMovie', game)
        
        self.setShader('oldMovie')        
        
        self.setTextureParameter('Noise', 'Noise2D_std.dds')
        
        self.setTimeMode(ScreenFilter.Time_0_X)
        self.setPredefinedParameter('time', ScreenFilter.Time)        
        
        self.setFloatParameter('Speed1', (0.02, 0.0, 0.0, 0.0))
        self.setFloatParameter('Speed2', (0.01, 0.0, 0.0, 0.0))
        self.setFloatParameter('IS', (0.01, 0.0, 0.0, 0.0))
        self.setFloatParameter('ScratchIntensity', (0.18, 0.0, 0.0, 0.0))
        self.setFloatParameter('flicker', (1919.95, 0.0, 0.0, 0.0))


class NegativeFilter(ScreenFilter):
    def __init__(self, game):
        ScreenFilter.__init__(self, 'Negative', game)        
        self.setShader('negative')


        
        

    
    