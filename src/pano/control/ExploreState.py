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

from direct.interval.IntervalGlobal import *

from constants import PanoConstants
from control.fsm import FSMState
from control.NodeScript import BaseNodeScript
from view.camera import CameraMouseControl
from control.PausedState import PausedState

class ExploreState(FSMState):
    
    NAME = 'exploreState'
    
    def __init__(self, gameRef = None):        
        FSMState.__init__(self, gameRef, ExploreState.NAME)        
        self.log = logging.getLogger('pano.exploreState')
        self.activeNode = None
        self.nodeScript = None    # script that controls the currently active node
        self.activeHotspot = None
        self.cameraControl = CameraMouseControl(self.getGame())
        self.sounds = None
        self.drawDebugViz = False
        
    def enter(self):
        
        FSMState.enter(self)
        
        game = self.getGame()
        self.drawDebugViz = game.getConfig().getBool(PanoConstants.CVAR_DEBUG_HOTSPOTS, False)
        
        self.cameraControl.initialize()        
                        
        # enable rotation of camera by mouse
        self.cameraControl.enable()
        
        game.getInput().addMappings('explore')
        self.sounds = game.getSoundsFx()
        
        if self.activeNode is None:
            self.changeDisplayNode(self.getGame().getInitialNode())
        else:            
            self.changeDisplayNode(self.activeNode.getName())
        
        game.getMusic().setPlaylist(game.getResources().loadPlaylist('main-music'))
#        game.getMusic().play()                        
        
    
    def registerMessages(self):
        return (
                PanoConstants.EVENT_GAME_RESUMED, 
                PanoConstants.EVENT_GAME_PAUSED,
                PanoConstants.EVENT_CHANGE_NODE,
                PanoConstants.EVENT_RESTORE_NODE
                )
    
    def doMouseAction(self):        
        if self.activeHotspot is not None:
            if self.log.isEnabledFor(logging.DEBUG):                    
                self.log.debug('Clicked on hotspot %s, (%s)', self.activeHotspot.getName(), self.activeHotspot.getDescription())
            
            if self.activeHotspot.hasAction():
                self.getGame().actions().execute(self.activeHotspot.getAction(), self.activeHotspot.getActionArgs())                
            self.getGame().getView().getTalkBox().showText(self.activeHotspot.getDescription(), 3.0)                                        
                                
    def exit(self):             
        FSMState.exit(self)
        
        if self.nodeTransition is not None:
            self.nodeTransition.finish()
            
        if self.nodeScript is not None:
            self.nodeScript.exit()
                    
        self.getGame().getInput().removeMappings('explore')        
        self.cameraControl.disable()                        
    
    def update(self, millis):
        if not self.getGame().isPaused():
            self.cameraControl.update(millis)
            
            # returns the face code and image space coordinates of the hit point    
            result = self.getGame().getView().raycastNodeAtMouse()
            if result is not None:
                face, x, y = result        
                dim = self.getGame().getView().panoRenderer.getFaceTextureDimensions(face)
                x *= dim[0]
                y *= dim[1]
                
                self.activeHotspot = None
                for h in self.activeNode.getHotspots():
                    if h.getFace() == face and x >= h.getXo() and x <= h.getXe() and y >= h.getYo() and y <= h.getYe():
                        self.activeHotspot = h
                        
                if self.activeHotspot is not None:
                    cu = self.activeHotspot.getCursor()
                    if cu is not None:
                        self.getGame().getView().getMousePointer().setByName(cu)
                else:
                    self.getGame().getView().getMousePointer().setByName('select')
                    
            if self.nodeScript is not None:
                self.nodeScript.update(millis)
    
    def suspend(self):        
        self.cameraControl.disable()
        self.nodeTransition.pause()
    
    def resume(self):
        self.cameraControl.enable()
        self.nodeTransition.resume()
    
    def onMessage(self, msg, *args):
        
        if self.nodeScript is not None:
            self.nodeScript.onMessage(msg, args)
        
        if msg == PanoConstants.EVENT_GAME_PAUSED:                        
            self.suspend()            
        elif msg == PanoConstants.EVENT_GAME_RESUMED:            
            self.resume()
        elif msg == PanoConstants.EVENT_CHANGE_NODE:
            node = args[0]
            self.log.debug('Got message to go to node %s' % node)
            self.changeDisplayNode(node, 1.0)                    
            
    def onInputAction(self, action):
        if action == "acMouseAction":
            self.doMouseAction()
        elif action == "save":            
            self.getGame().requestSave(('my_save'))            
        elif action == "load":
            self.getGame().requestLoad(('my_save')) #_Fri_Mar_20_121647_2009.sav'))
        else:
            return False if self.nodeScript is None else self.nodeScript.onInputAction(action)
        return True
    
    def persistState(self, persistence):
        ctx = persistence.createContext('exploreState_ctx')
        ctx.addVar('node', self.activeNode.getName())
                
        if self.nodeScript is not None:
            nodescriptCtx = self.nodeScript.persistState(persistence)
            ctx.addVar('nodescript', persistence.serializeContext(nodescriptCtx))                        
        
        return ctx
    
    def restoreState(self, persistence, ctx):
        nodeName = ctx.getVar('node')
        node = self.getGame().getResources().loadNode(nodeName)
        
        self._loadNode(nodeName)
        
        nodescriptCtx = ctx.getVar('nodescript')
        self.nodeScript.restoreState(persistence, persistence.deserializeContext(nodescriptCtx))        
    
    def changeDisplayNode(self, newNodeName, fadeDuration = 1.0):
        '''
        Displays the specified node and fades in & out the screen in fadeDuration seconds.        
        '''

        # dispose old node and load new
        self._loadNode(newNodeName)
        
        # display node in a number of steps
        game = self.getGame()
        self.nodeTransition = Sequence(
                                        Func(game.getView().fadeOut, fadeDuration / 2.0),
                                        Wait(0.2 + fadeDuration / 2.0),
                                        Func(game.getView().displayNode, self.activeNode),                                    
                                        Func(game.getView().mousePointer.setByName, "select"),
                                        Func(game.getView().panoRenderer.drawDebugHotspots, self.drawDebugViz),
                                        Func(self._setCameraLookAt, self.activeNode.getLookAt()),
                                        Func(self._safeCallEnter),
                                        Func(game.getView().fadeIn, fadeDuration / 2.0),
                                        Wait(fadeDuration / 2.0),
                                        Func(self._completeNodeTransition),
                                        name = 'Node transition sequence'
                                        )
        self.nodeTransition.start()         
        
    def _loadNode(self, nodeName, forceReload = False):
        '''
        Loads the node specified by the given name while disposing the old node in the process.
        '''
        if self.activeNode is not None and nodeName == self.activeNode.getName() and not forceReload:
            return
        
        if self.nodeScript is not None:
            self.nodeScript.exit()
            self.nodeScript = None
            
        # delete class definition and script object from the global context
        # the name of the node script class must match the filename into which it is defined
        if self.activeNode is not None:
            oldScriptName = self.activeNode.getScriptName()
            if oldScriptName is not None:
                if __builtins__.has_key(oldScriptName):
                    del __builtins__[oldScriptName]
#        
#                # verify
#                if locals().has_key(oldScriptName + '_obj'):
#                    self.log.error('Failed to clean old node script object instance and definition from the local context')        

        # loads the node script and inserts it in the builtins for global access
        game = self.getGame()
        self.activeNode = game.getResources().loadNode(nodeName)
        if self.activeNode is None:
            print 'Warning failed to load node ' , nodeName
            
        if self.activeNode.getScriptName() is not None:
            scriptPath = game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_SCRIPTS, self.activeNode.getScriptName() + '.py')
            if scriptPath is not None:
                self.log.debug('Executing script file %s' % scriptPath)
                fp = None
                try:
                    fp = open(scriptPath, 'r')
                    exec(fp)
                except IOError:
                    self.log.exception('Error reading script file %s' % scriptPath)
                finally:
                    if fp is not None:
                        fp.close()
                        
                exec('__builtins__[' + self.activeNode.getScriptName() + '] = ' + self.activeNode.getScriptName())                
                exec('self.nodeScript  = ' + self.activeNode.getScriptName() + '(game)')
                __builtins__['nodescript'] = self.nodeScript                
                
                # verify that the node script object extends FSMState
                assert isinstance(self.nodeScript, BaseNodeScript), 'Node script object must subclass pano.control.FSMState'
                       
        
    def _setCameraLookAt(self, lookat):
        '''
        Points the camera to the specified look-at point.
        This point is defined through a string parameter which can take one of the following values:
          a) face_xxxx, where xxxx can be front, back, left, right, top or bottom and denotes the center of the respective face of the cube node.
          b) hotspot_xxx, where xxxx is the name of a hotspot defined within the context of the active node.
        '''
        wp = None
        if lookat.startswith('face_'):
            faceName = lookat[5:]
            face = PanoConstants.CBM_FRONT_FACE
            if faceName == 'front':
                face = PanoConstants.CBM_FRONT_FACE
            elif faceName == 'back':
                face = PanoConstants.CBM_BACK_FACE
            elif faceName == 'right':
                face = PanoConstants.CBM_RIGHT_FACE
            elif faceName == 'left':
                face = PanoConstants.CBM_LEFT_FACE
            elif faceName == 'top':
                face = PanoConstants.CBM_TOP_FACE
            elif faceName == 'bottom':
                face = PanoConstants.CBM_BOTTOM_FACE
            else:
                self.log.error('Wrong lookat attribute: %s for node %s' % (lookat, self.activeNode.getNode()))
                return
            
            wp = self.getGame().getView().panoRenderer.getWorldPointFromFacePoint(face, (0.5, 0.5))
            
        elif lookat.startswith('hotspot_'):
            hpName = lookat[8:]
            hp = self.activeNode.getHotspot(hpName)
            wp = self.getGame().getView().panoRenderer.getHotspotWorldPos(hp)
                        
        if wp is not None:
            camera = self.getGame().getView().panoRenderer.getCamera()
            camera.lookAt(wp[0], wp[1], wp[2])
        
    def _safeCallEnter(self):
        if self.nodeScript is not None:
            self.nodeScript.enter()
        
    def _completeNodeTransition(self):
        '''
        The final step of the transition sequence for displaying a new node. 
        This function primarily exists in order to ensure that a cleanup function can be called when the
        transition sequence is abruptly ended by calling sequence.finish()
        '''
        if self.getGame().getView().getActiveNode() != self.activeNode:
            self.log.warning('The node transition sequence did not complete. Displaying node %s while having %s as active' % (self.getGame().getActiveNode(), self.activeNode)) 
        

    