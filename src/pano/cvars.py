import re

class ConfigVars:
    
    def __init__(self):    
        self.cvars = {}      
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
            return self.cvars[var] == 'True'
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
    
    
    