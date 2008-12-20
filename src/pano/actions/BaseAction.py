class BaseAction:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def getName(self):
        return self.name
    
    def getDescription(self):
        return self.description
        
    def execute(self, game):
        pass