
class PanoParameters:

    # speed of camera horizontal rotation in degrees/second when moving the mouse
    CAM_CONTROL_HROT_SPEED = 'CAM_CONTROL_HROT_SPEED'
        
    # speed of camera vertical rotation in degrees/second when moving the mouse    
    CAM_CONTROL_VROT_SPEED = 'CAM_CONTROL_VROT_SPEED'

    def __init__(self):    
        self.params = {}
        self.addParam(PanoParameters.CAM_CONTROL_HROT_SPEED, 40)
        self.addParam(PanoParameters.CAM_CONTROL_VROT_SPEED, 40)
        
    def addParam(self, paramName, paramValue):
        self.params[paramName] = paramValue
        
    def removeParam(self, paramName):
        self.params.pop(paramName, '')
        
    def getParam(self, paramName):
        return self.params[paramName]
        
    
    
    