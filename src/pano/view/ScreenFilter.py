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
import math

from direct.filter.FilterManager import FilterManager
from pandac.PandaModules import NodePath
from pandac.PandaModules import Texture
from pandac.PandaModules import Vec4
from pandac.PandaModules import Mat4

class ScreenFilter(object):
    
    # modes for cycling time 
    Time_0_X   = 1   # time cycles between 0 and the time period
    Time_0_1   = 2   # time cycles between 0 and 1
    Time_0_2PI = 3   # time cycles between 0 and 2*PI    
    
    # names of predefined shader parameters
    Cos_Time_0_X   = 1
    Sin_Time_0_X   = 2
    Tan_Time_0_X   = 3
    Cos_Time_0_1   = 4 
    Sin_Time_0_1   = 5
    Tan_Time_0_1   = 6
    Cos_Time_0_2PI = 7
    Sin_Time_0_2PI = 8
    Tan_Time_0_2PI = 9
    Time           = 10
    Time_Period    = 11
    
    '''
    Represents a screen based image effect. Every filter must have a unique name.
    '''
    def __init__(self, name = '', game = None):
        self.log = logging.getLogger('pano.screenFilter')
        self.name = name
        self.game = game
        
        self.postProcess = None
        self.screenQuad = None
        self.enabled = False
    
        self.shader = None
        
        # parameters by type
        self.texParams = {}
        self.floatParams = {}
        self.matParams = {}
        self.predefinedParams = {}
        
        self.nodesRoot = None
    
        self.time = 0.0
        self.timePeriod = 120.0 # in seconds
        self.timeMode = self.Time_0_X
        
    def getShader(self):
        '''
        Returns the base name of the shader effect file.  
        '''
        return self.shader
    
    
    def setShader(self, shader):
        '''
        Sets the base name of the shader effect file.  
        '''
        differ = self.shader != shader
        self.shader = shader
        
        if self.isEnabled() and differ:
            self.disable()
            self.enable()
        
        
    def enable(self):
        '''
        Enables the filter. It is assumed that after this operation the rendering operation
        has been altered such that the filter effects will be visible. 
        '''
        if self.isEnabled(): 
            return
         
        shader = self.game.getResources().loadShader(self.shader)
        if shader is not None:            
            self.postProcess = FilterManager(self.game.getView().getWindow(), self.game.getView().panoRenderer.getCamera())
            self.postProcess.windowEvent(self.game.getView().getWindow())   # auto resize buffers when window resizes
            tex = Texture()
            self.screenQuad = self.postProcess.renderSceneInto(colortex = tex)
            self.screenQuad.setShader(shader)
            self.screenQuad.setShaderInput("tex", tex)
            self._applyShaderInputs()
            self.enabled = True            
        else:
            self.log.error('failed to set screen filter BlackAndWhite because shader %s was not found' % filterName)
    
    
    def disable(self):
        '''
        Disables the filter, thereby eliminating the effects of the filter from the rendering
        of the scene. Any graphics resources should also get released here as well because the
        filter might never get enabled again.
        '''
        if not self.enabled: return
                
        if self.postProcess is not None:
            self._cleanUpShaderInputs()
            self.postProcess.cleanup()
            self.postProcess = None
        self.screenQuad = None
        self.enabled = False
    
    
    def update(self, millis):
        '''
        Updates the state of the filter, assuming the given amount of milliseconds have elapsed.
        '''
#        self.log.debug('updating with %f millis' % millis)
        self.time += millis / 1000.0
        if self.time > self.timePeriod:
            self.time -= self.timePeriod
        self._applyPredefinedInputs()
    
    
    def isEnabled(self):
        '''
        Return True if this filter has been enabled or False if otherwise.
        '''
        return self.enabled 
    
    
    def getTimeMode(self):
        '''
        Returns the time cycling mode.
        '''
        return self.timeMode
    
    
    def setTimeMode(self, mode):
        '''
        Sets the time cycling mode.
        '''
        self.timeMode = mode
    
    
    def getRenderTarget(self):
        '''
        Returns the screen aligned quad model instance associated with this filter or None if the filter isn't active.
        '''
        return self.screenQuad
    
    
    def getShader(self):
        '''
        Returns the Shader instance associated with this filter or None if the filter isn't active.
        '''
        return self.screenQuad.getShader() if self.screenQuad is not None else None
    
    
    def setTextureParameter(self, name, filename):
        '''
        Sets a named texture parameter which will be accessible to the shader via the input
        uniform sampler2D 'k_<name>'.
        See Panda3D Manual: List of Possible Shader Inputs for more details
        '''
        self.texParams[name] = filename
    
    
    def setFloatParameter(self, name, value):
        '''
        Sets a named vector of floats parameter which will be accessible to the shader via the input
        uniform float4 'k_<name>'.
        See Panda3D Manual: List of Possible Shader Inputs for more details
         
        Note: The value parameter must be a tuple or list with at least 4 elements.        
        '''
        self.floatParams[name] = value
    
    
    def setMatrixParameter(self, name, mat):
        '''
        Sets a named 4x4 matrix parameter which will be accessible to the shader via the input
        uniform float4x4 'k_<name>'.
        See Panda3D Manual: List of Possible Shader Inputs for more details
         
        Note: The value parameter must be a tuple or list with at least 16 elements.        
        '''        
        self.matParams[name] = mat
        
        
    def setPredefinedParameter(self, name, value):
        '''
        Sets a named float4 parameter with a predefined semantic and which will be accessible to the shader 
        via the input uniform float4 'k_<name>'.
        See Panda3D Manual: List of Possible Shader Inputs for more details                 
        '''
        self.predefinedParams[name] = value
    
    
    def getTextureParameter(self, name):
        '''
        Returns the texture input associated with the given name or None if no such input exists.
        '''
        return self.texParams.get(name)
    
    
    def getFloatParameter(self, name):
        '''
        Returns the vector of floats input associated with the given name or None if no such input exists.
        '''
        return self.floatParams.get(name)
    
    
    def getMatrixParameter(self, name):
        '''
        Returns the 4x4 matrix input associated with the given name or None if no such input exists.
        '''
        return self.matParams.get(name)
    
    
    def getPredefinedParameter(self, name):
        '''
        Returns the float4 input associated with the given name or None if no such input exists.
        '''
        return self.predefinedParams.get(name)
    
    
    def _applyShaderInputs(self):
        '''
        Applies the specified texture, vector and matrix shader inputs.
        Note: Matrix inputs are applied to a shader through a NodePath whose local transformation matches the matrix.
        '''
        for param, texName in self.texParams.items():
            tex = self.game.getResources().loadTexture(texName)
            if tex is not None:
                tex.setWrapU(Texture.WMRepeat)
                tex.setWrapV(Texture.WMRepeat)
                self.screenQuad.setShaderInput(param, tex)
            else:
                self.log.error('Failed to set shader input %s because the texture was not found' % texName)
                
        for param, val in self.floatParams.items():            
            self.screenQuad.setShaderInput(param, Vec4(val[0], val[1], val[2], val[3]))

        if self.nodesRoot is None:
            self.nodesRoot = render.attachNewNode('k_matrices')
    
        for param, val in self.matParams.items():
            np = NodePath()
            np.setName(param + '_transform')
            mat = Mat4()
            for i in range(4):                
                mat.setRow(i, Vec4(val[i*4+1], val[i*4+2], val[i*4+3], val[i*4+4]))
            np.setMat(mat)
            np.reparentTo(self.nodesRoot)
            self.screenQuad.setShaderInput(param, np)
            
        self._applyPredefinedInputs()
    
    
    def _applyPredefinedInputs(self):
        for param, val in self.predefinedParams.items():
            if val == self.Time:
                self.screenQuad.setShaderInput(param, Vec4(self._convertTime(self.timeMode), 0, 0, 0))                
            
            elif val == self.Cos_Time_0_X:
                self.screenQuad.setShaderInput(param, Vec4(math.cos(self.time), 0, 0, 0))
            elif val == self.Sin_Time_0_X:
                self.screenQuad.setShaderInput(param, Vec4(math.sin(self.time), 0, 0, 0))
            elif val == self.Tan_Time_0_X:
                self.screenQuad.setShaderInput(param, Vec4(math.tan(self.time), 0, 0, 0))
                
            elif val == self.Cos_Time_0_1:
                self.screenQuad.setShaderInput(param, Vec4(math.cos(self._convertTime(self.Time_0_1), 0, 0, 0)))
            elif val == self.Sin_Time_0_1:
                self.screenQuad.setShaderInput(param, Vec4(math.sin(self._convertTime(self.Time_0_1), 0, 0, 0)))
            elif val == self.Tan_Time_0_1:
                self.screenQuad.setShaderInput(param, Vec4(math.tan(self._convertTime(self.Time_0_1), 0, 0, 0)))
                
            elif val == self.Cos_Time_0_2PI:
                self.screenQuad.setShaderInput(param, Vec4(math.cos(self._convertTime(self.Time_0_2PI), 0, 0, 0)))
            elif val == self.Sin_Time_0_2PI:
                self.screenQuad.setShaderInput(param, Vec4(math.sin(self._convertTime(self.Time_0_2PI), 0, 0, 0)))
            elif val == self.Tan_Time_0_2PI:
                self.screenQuad.setShaderInput(param, Vec4(math.tan(self._convertTime(self.Time_0_2PI), 0, 0, 0)))
                
            elif val == self.Time_Period:
                self.screenQuad.setShaderInput(param, Vec4(self.timePeriod, 0, 0, 0))
                
    
    def _cleanUpShaderInputs(self):
        for param in self.texParams.keys():
            self.screenQuad.clearShaderInput(param)        
            
        for param in self.floatParams.keys():
            self.screenQuad.clearShaderInput(param)
            
        for param in self.matParams.keys():
            self.screenQuad.clearShaderInput(param)
            
        for param in self.predefinedParams.keys():
            self.screenQuad.clearShaderInput(param)
            
        self.nodesRoot.removeNode()
        self.nodesRoot = None
        
        
    def _convertTime(self, toMode):
        '''
        Converts the accumulated time, stored in self.time, to the given mode.
        It is assumed that self.time is always in the range 0..X, where X is the time period.
        '''
        if toMode == self.Time_0_1:
#            self.log.debug('converting time %f to 0..1 range as %f' % (self.time, self.time / self.timePeriod))
            return self.time / self.timePeriod
        elif toMode == self.Time_0_2PI:
#            self.log.debug('converting time %f to 0..2PI range as %f' % (self.time, 2.0*math.pi*self.time / self.timePeriod))
            return 2.0*math.pi*(self.time / self.timePeriod)
        else:
            return self.time
        
    
    
class CompositeFilter(ScreenFilter):
    '''
    A filter that composites the output of a group of filters.
    TODO:Implement this class.
    '''
    pass
