from direct.showbase import DirectObject

from control.fsm import FSMState
from view.camera import CameraMouseControl

class ExploreState(FSMState, DirectObject.DirectObject):

    NAME = 'ExploreState'
    
    def __init__(self, gameRef = None, node = None):
        FSMState.__init__(self, gameRef, 'ExploreState')
        self.activeNode = None
        self.cameraControl = CameraMouseControl(self.getGame())
        
    def enter(self):
        
        print 'entered explore state'
        
        #setup event handlers
        self.accept('mouse1', self.onLeftClick)
        
        # enable rotation of camera by mouse
        self.cameraControl.enable()

        self.activeNode = self.getGame().getView().getActiveNode()        
    
    def onLeftClick(self):
        # returns the face code and image space coordinates of the hit point    
        face, x, y = self.getGame().getView().raycastNodeAtMouse()
        x *= 1024
        y *= 1024
        for h in self.activeNode.getHotspots():
            if h.getFace() == face and x >= h.getXo() and x <= h.getXe() and y >= h.getYo() and y <= h.getYe():
                print 'Clicked on hotspot ' + h.getName() + ', (' + h.getDescription() + ')'
                self.getGame().actions().execute(h.getAction(), h.getActionParams())                 
    
    def exit(self):     
        # unregister from Panda's event system   
        self.ignoreAll()
        
        self.cameraControl.disable()
    
    def update(self, millis):
        self.cameraControl.update(millis)
    