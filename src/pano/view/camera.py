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

from cvars import ConfigVars
from constants import PanoConstants

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
        self.active = False
        
    def initialize(self):
        self.active = False
        self.mouseHSpeed = self.game.getConfig().getFloat(PanoConstants.CVAR_CAM_HSPEED)
        self.mouseVSpeed =  self.game.getConfig().getFloat(PanoConstants.CVAR_CAM_VSPEED)

    def isActive(self):
        return self.active


    def getMouseHSpeed(self):
        return self.mouseHSpeed


    def getMouseVSpeed(self):
        return self.mouseVSpeed


    def setIsActive(self, value):
        self.active = value


    def setMouseHSpeed(self, value):
        self.mouseHSpeed = value


    def setMouseVSpeed(self, value):
        self.mouseVSpeed = value        
        
    def enable(self):
        """
        The controller is activated and any mouse movement will result in a change to the camera's orientation. 
        """        
        self.active = True
        
    def disable(self):
        """
        The camera will not be affected anymore by this controller.
        """        
        self.active = False
        
    def update(self, millisElapsed):
        """
        Rotates the camera based on the position of the mouse cursor. When the mouse cursor is inside one of four
        predefined screen regions, a rotation is triggered. The regions are top, left, bottom and right. The top
        and bottom regions trigger a vertical rotation upwards and downwards respectively. While the left and
        right regions trigger a horizontal rotation leftwards and rightwards.
        The speed of rotation is controlled by the fields self.mouseHSpeed and self.mouseVSpeed and is frame depended
        by multiplying it with the elapsed time since the last update.
        """
        if not self.active:
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
            secs = millisElapsed / 1000.0
            if relX >= self.topX and relX <= (self.topX + self.topWidth) and relY >= self.topY and relY <= (self.topY + self.topHeight):
                # Rotate around the global X axis in a counter-clockwise fashion                
                x_rot = -self.mouseVSpeed * secs
                
            elif relX >= self.bottomX and relX <= (self.bottomX + self.bottomWidth) and relY >= self.bottomY and relY <= (self.bottomY + self.bottomHeight):
                # Rotate around the global X axis in a clockwise fashion                
                x_rot = self.mouseVSpeed * secs
            
            # check for left-right camera movement
            if relX >= self.leftX and relX <= (self.leftX + self.leftWidth) and relY >= self.leftY and relY <= (self.leftY + self.leftHeight):
                # Rotate around the global Y axis in a counter-clockwise fashion                
                y_rot = self.mouseHSpeed * secs
                
            elif relX >= self.rightX and relX <= (self.rightX + self.rightWidth) and relY >= self.rightY and relY <= (self.rightY + self.rightHeight):
                # Rotate around the global Y axis in a clockwise fashion            
                y_rot = -self.mouseHSpeed * secs
            
            hpr = base.camera.getHpr()            
            base.camera.setHpr((hpr[0] + y_rot) % 360, (hpr[1] + x_rot) % 360, hpr[2])            


