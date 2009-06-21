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

import re

class ConfigVars:
    
    def __init__(self):    
        self.cvars = {}
        self.vec2Re = re.compile(r'\s*(\S+)\s+(\S+)\s*')      
        self.vec3Re = re.compile(r'\s*(\S+)\s+(\S+)\s+(\S+)\s*')
        self.vec4Re = re.compile(r'\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*')  
        
    def add(self, var, value):
        self.cvars[var] = value
        
    def remove(self, var):
        if self.cvars.has_key(var):
            self.cvars.pop(var, '')
        
    def get(self, var, default = None):
        if self.cvars.has_key(var):
            return self.cvars[var]
        else:
            return default
    
    def getBool(self, var, default = None):
        if self.cvars.has_key(var):
            return str.lower(self.cvars[var]) == 'true'
        else:
            return default
    
    def getFloat(self, var, default = None):
        if self.cvars.has_key(var):
            return float(self.cvars[var])
        else:
            return default
    
    def getInt(self, var, default = None):
        if self.cvars.has_key(var):
            return int(self.cvars[var])
        else:
            return default
        
    def getList(self, var, default = None):
        """
        Reads a list of comma separated string values.
        """
        if self.cvars.has_key(var):
            value = self.cvars[var]
            if value is not None:
                return value.split(',')
            return None
        else:
            return default
        
    def getVec2(self, var, default = None):
        if self.cvars.has_key(var):
            value = self.cvars[var]
            if value is not None:
                m = self.vec2Re.match(value)
                if m is not None:
                    return (float(m.group(1)), float(m.group(2)))
            return None
        else:
            return default
        
    def getVec3(self, var, default = None):
        if self.cvars.has_key(var):
            value = self.cvars[var]
            if value is not None:
                m = self.vec3Re.match(value)
                if m is not None:
                    return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
            return None
        else:
            return default
    
    def getVec4(self, var, default = None):
        if self.cvars.has_key(var):
            value = self.cvars[var]
            if value is not None:
                m = self.vec4Re.match(value)
                if m is not None:                    
                    return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
            return None
        else:
            return default
    
    
    