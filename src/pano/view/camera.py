import logging

from parameters import PanoParameters

class CameraMouseControl:
    """
    Controls the player's camera using the mouse.
    When this camera controller is active it will rotate the view
    camera accordingly when the mouse enters four specific screen
    regions: 
    The top region rotates the camera around the world X axis
    in a clockwise fashion thus allowing the user to view higher parts
    of the environment.
    The bottom region rotates the camera around the world X axis
    in a anti-clockwise fashion and thus the user can view lower.
    Similarly the left region rotates the camera around the world
    Z axis in a anti-clockwise fashion allowing the user to turn
    the camera to the left.
    Finally the right region rotates the camera around the world
    Z axis in a clockwise fashion allowing the user to turn
    the camera to the right.
    All regions are rectangular and specified in relative screen
    coordinates.
    """
    
    
    #Origin and dimensions of the top region
    topX = 0
    topY = 0
    topWidth = 1.0
    topHeight = 0.2
        
    bottomX = 0
    bottomY = 0.9
    bottomWidth = 1.0
    bottomHeight = 0.1
    
    leftX = 0
    leftY = 0.2
    leftWidth = 0.2
    leftHeight = 0.7
    
    rightX = 0.8
    rightY = 0.2
    rightWidth = 0.2
    rightHeight = 0.7
    
    def __init__(self, gameRef):
        self.log = logging.getLogger('pano.camera')
        self.game = gameRef
        self.isActive = False
        self.mouseHSpeed = self.game.parameters.getParam(PanoParameters.CAM_CONTROL_HROT_SPEED)
        self.mouseVSpeed =  self.game.parameters.getParam(PanoParameters.CAM_CONTROL_VROT_SPEED)
        
    def enable(self):
        """
        The controller is activated and any mouse movement will result in a change to the camera's orientation. 
        """        
        self.isActive = True
        
    def disable(self):
        """
        The camera will not be affected anymore by this controller.
        """        
        self.isActive = False
        
    def update(self, millisElapsed):
        """
        Rotates the camera based on the position of the mouse cursor. When the mouse cursor is inside one of four
        predefined screen regions, a rotation is triggered. The regions are top, left, bottom and right. The top
        and bottom regions trigger a vertical rotation upwards and downwards respectively. While the left and
        right regions trigger a horizontal rotation leftwards and rightwards.
        The speed of rotation is controlled by the fields self.mouseHSpeed and self.mouseVSpeed and is frame depended
        by multiplying it with the elapsed time since the last update.
        """
        if not self.isActive:
            return
        
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            
            pr = base.win.getProperties()
            winWidth = pr.getXSize()
            winHeight = pr.getYSize()
            #relX = (1.0 * x) / winWidth
            #relY = (1.0 * y) / winHeight
            relX = (x + 1.0) / 2.0
            relY = (y + 1.0) / 2.0
            
            x_rot = 0.0
            y_rot = 0.0
                        
            # check for up-down camera movement
            if relX >= self.topX and relX <= (self.topX + self.topWidth) and relY >= self.topY and relY <= (self.topY + self.topHeight):
                # Rotate around the global X axis in a counter-clockwise fashion                
                x_rot = -self.mouseVSpeed * millisElapsed
                
            elif relX >= self.bottomX and relX <= (self.bottomX + self.bottomWidth) and relY >= self.bottomY and relY <= (self.bottomY + self.bottomHeight):
                # Rotate around the global X axis in a clockwise fashion                
                x_rot = self.mouseVSpeed * millisElapsed
            
            # check for left-right camera movement
            if relX >= self.leftX and relX <= (self.leftX + self.leftWidth) and relY >= self.leftY and relY <= (self.leftY + self.leftHeight):
                # Rotate around the global Y axis in a counter-clockwise fashion                
                y_rot = self.mouseHSpeed * millisElapsed
                
            elif relX >= self.rightX and relX <= (self.rightX + self.rightWidth) and relY >= self.rightY and relY <= (self.rightY + self.rightHeight):
                # Rotate around the global Y axis in a clockwise fashion            
                y_rot = -self.mouseHSpeed * millisElapsed
            
            hpr = base.camera.getHpr()            
            base.camera.setHpr((hpr[0] + y_rot) % 360, (hpr[1] + x_rot) % 360, hpr[2])            
