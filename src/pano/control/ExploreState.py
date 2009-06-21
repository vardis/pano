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

from pano.constants import PanoConstants
from pano.control.fsm import FSMState
from pano.control.NodeScript import BaseNodeScript

class ExploreState(FSMState):
    '''
    Controls the state of the game when displaying a node and allow the user to interact with the environment.
    '''
    def __init__(self, gameRef = None):        
        FSMState.__init__(self, gameRef, PanoConstants.STATE_EXPLORE)        
        self.log = logging.getLogger('pano.exploreState')
        self.activeNode = None
        self.nodeScript = None    # script that controls the currently active node
        self.activeHotspot = None
        self.sounds = None
        self.drawDebugViz = False
        self.nodeTransition = None
        
        # if True then we are transitioning to a new node, we use this flag to reject certain operations
        # while it is true
        self.inTransition = False
        
    def enter(self):
        
        FSMState.enter(self)
        
        self.drawDebugViz = self.game.getConfig().getBool(PanoConstants.CVAR_DEBUG_HOTSPOTS, False)
        
        self.game.getInput().addMappings('explore')
        self.sounds = self.game.getSoundsFx()
        
        if self.activeNode is None:
            self.changeDisplayNode(self.game.getInitialNode())
        else:            
            self.changeDisplayNode(self.activeNode.name)
        
    
    def registerMessages(self):
        return (
                PanoConstants.EVENT_GAME_RESUMED, 
                PanoConstants.EVENT_GAME_PAUSED,
                PanoConstants.EVENT_CHANGE_NODE,
                PanoConstants.EVENT_RESTORE_NODE
                )
    
    def onHotspotAction(self):
        '''
        Handles the action input event when targeted to hot-spots.
        When no active item exists, the input event will trigger the execution of the action associated
        with the hot-spot as defined in the definition file of the node and a message will be emitted
        to notify about the action event. 
        When however there is an active item from the inventory and the hot-spot is flagged to interact
        with items, then a message is emitted to notify about the interaction between item and hot-spot.
        '''        
        if self.activeHotspot is not None:
            if self.log.isEnabledFor(logging.DEBUG):                    
                self.log.debug('Clicked on hotspot %s, (%s)', self.activeHotspot.name, self.activeHotspot.description)
                        
            activeItem = self.game.getInventory().getActiveItem()
            if self.activeHotspot.itemInteractive and activeItem is not None: 
                self.getMessenger().sendMessage(PanoConstants.EVENT_HOTSPOT_ITEM_INTERACTION, [self.activeHotspot, activeItem])
                
            else:                            
                if self.activeHotspot.hasAction():
                    self.game.actions().execute(self.activeHotspot.action, *self.activeHotspot.actionArgs)                                            
            
                # send message to notify about interaction with this hotspot
                self.log.debug('sending hotspot action msg')
                self.getMessenger().sendMessage(PanoConstants.EVENT_HOTSPOT_ACTION, [self.activeHotspot])    
            
    def onHotspotLookAt(self):                                    
        if self.activeHotspot is not None:
            if self.log.isEnabledFor(logging.DEBUG):                    
                self.log.debug('Looked at hotspot %s, (%s)', self.activeHotspot.name, self.activeHotspot.description)
                
            self.game.getView().getTalkBox().showText(self.activeHotspot.description, 3.0)
            self.getMessenger().sendMessage(PanoConstants.EVENT_HOTSPOT_LOOKAT, [self.activeHotspot])
                                
    def exit(self):             
        FSMState.exit(self)
        
        if self.nodeTransition is not None:
            self.nodeTransition.finish()
            self.inTransition = False
            
        if self.nodeScript is not None:
            self.nodeScript.exit()
                    
        self.game.getInput().removeMappings('explore')        
        self.game.getView().getCameraController().disable()   
        self.game.getView().clearScene()    
        self.game.getView().getMousePointer().hide()      
        self.game.getView().getTalkBox().hide()
        
        self.game.getMusic().stop()            
    
    def update(self, millis):
        
        if not self.game.isPaused() and (self.nodeTransition is None or not self.nodeTransition.isPlaying()):
                        
            # returns the face code and image space coordinates of the hit point
            # TODO: change raycaster to target hotspots and return hotspots directly instead of face, x, y...
            activeItem = self.game.getInventory().getActiveItem()            
            hotspots = self.game.getView().raycastNodeAtMouse()
            if hotspots is not None:
                
                # reset
                self.activeHotspot = None
                
                for hp in hotspots:
                    if hp.active:
                        self.activeHotspot = hp
                        break 
#                face, x, y = result        
#                dim = self.game.getView().panoRenderer.getFaceTextureDimensions(face)
#                x *= dim[0]
#                y *= dim[1]                
                
#                self.activeHotspot = None
#                for h in self.activeNode.getHotspots():
#                    if h.face == face and x >= h.xo and x <= h.xe and y >= h.yo and y <= h.ye and h.active:
#                        self.activeHotspot = h
                                                                             
                if self.activeHotspot is not None:
                    # if there is an item selected from the inventory and the hotspot is flagged to interact with items,
                    # then leave the cursor unchanged. Otherwise set the mouse pointer specified by the hotspot.                    
                    if activeItem is None or not self.activeHotspot.itemInteractive:
                        cu = self.activeHotspot.cursor
                        if cu is not None:
                            self.game.getView().getMousePointer().setByName(cu)
                    else:
                        self.game.getView().getMousePointer().setImageAsPointer(activeItem.getSelectedImage(), 0.3)
                        
                elif activeItem is None:
                    self.game.getView().getMousePointer().setByName('select')
                    
            if self.nodeScript is not None and not self.inTransition:
                self.nodeScript.update(millis)
            
            self.inTransition = False 
            self.nodeTransition = None  
            
    
    def suspend(self):        
        self.game.getView().getCameraController().disable()
        if self.nodeTransition != None:
            self.nodeTransition.pause()
    
    def resume(self):
        self.game.getView().getCameraController().enable()
        if self.nodeTransition != None:            
            self.nodeTransition.resume()
    
    def onMessage(self, msg, *args):        
        if self.inTransition:
            return
        
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
        if self.inTransition:
            return False
        
        if action == "acMouseAction":
            self.onHotspotAction()
        elif action == "acMouseLook":
            # if there is an active item in the inventory then this action will correspond to reseting the active item
            # and the mouse cursor. Otherwise we perform a look-at operation on the active hotspot, if any.
            if self.game.getInventory().getActiveItem() is not None:
                self.game.getView().getMousePointer().setByName('select')
                self.game.getInventory().setActiveItem(None)
            else:
                self.onHotspotLookAt()
        elif action == "save":            
            self.game.requestSave(('my_save'))            
        elif action == "load":
            self.game.requestLoad(('my_save')) #_Fri_Mar_20_121647_2009.sav'))
        elif action == "post_process_filter":
            self.game.getView().getPostProcess().enableFilter('Negative')
        elif action == "clear_post_process_filter":
            self.game.getView().getPostProcess().disableFilter('Negative')
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
        
        self._loadNode(nodeName, forceReload = True)
        
        nodescriptCtx = ctx.getVar('nodescript')
        self.nodeScript.restoreState(persistence, persistence.deserializeContext(nodescriptCtx))        
    
    def changeDisplayNode(self, newNodeName, fadeDuration = 1.0):
        '''
        Displays the specified node and fades in & out the screen in fadeDuration seconds.        
        '''

        # dispose old node and load new
        self._loadNode(newNodeName)
        
        if self.activeNode is None:
            return
        
        # camera mouse controlled only in 3D nodes
        if self.activeNode.is2D():
            self.game.getView().getCameraController().disable()
        else:
            self.game.getView().getCameraController().enable()
        
        # display node in a number of steps
        self.nodeTransition = Sequence(
                                        Func(self.game.initGameSequence),
                                        Func(self.game.getView().fadeOut, fadeDuration / 2.0),
                                        Wait(0.2 + fadeDuration / 2.0),
                                        Func(self._safeCallPreDisplay),
                                        Func(self.game.getView().displayNode, self.activeNode),                                    
                                        Func(self.game.getView().mousePointer.setByName, "select"),
                                        Func(self.game.getView().panoRenderer.drawDebugHotspots, self.drawDebugViz),
                                        Func(self._safeCallCameraLookAt),
                                        Func(self._safeCallEnter),
                                        Func(self.game.getView().fadeIn, fadeDuration / 2.0),
                                        Wait(fadeDuration / 2.0),
                                        Func(self._completeNodeTransition),
                                        Func(self.game.endGameSequence),
                                        name = 'Node transition sequence'
                                        )
        self.inTransition = True        
        self.nodeTransition.start()    
    
        
    def _loadNode(self, nodeName, forceReload = False):
        '''
        Loads the node specified by the given name while disposing the old node in the process.
        '''
        if self.activeNode is not None and nodeName == self.activeNode.name and not forceReload:            
            return
        
        self._unloadCurrentNode()

        # loads the node script    
        self.activeNode = self.game.getResources().loadNode(nodeName)
        if self.activeNode is None:
            self.log.error('Failed to load node %s' % nodeName)
            return
            
        if self.activeNode.getScriptName() is not None:
            scriptPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_SCRIPTS, self.activeNode.scriptName + '.py')
            if scriptPath is not None:
                self.log.debug('Executing script file %s' % scriptPath)
                d = {}
                fp = None
                try:
                    fp = open(scriptPath, 'r')                    
                    exec(fp, d, d)
                except IOError:
                    self.log.exception('Error reading script file %s' % scriptPath)
                finally:
                    if fp is not None:
                        fp.close()
                                       
                exec('self.nodeScript  =  d[self.activeNode.getScriptName()] (self.game, self.activeNode)')                            
                
                # verify that the node script object extends BaseNodeScript
                assert isinstance(self.nodeScript, BaseNodeScript), 'Node script object must subclass pano.control.FSMState'
                
                # restore any previously persisted state
                self._restoreNodescriptState()
                       
                       
    def _unloadCurrentNode(self):
        if self.nodeScript is not None:
            self._persistNodescriptState()
            self.nodeScript.exit()
            self.nodeScript = None
            
        # delete class definition and script object from the global context
        # the name of the node script class must match the filename into which it is defined
        if self.activeNode is not None:
            oldScriptName = self.activeNode.scriptName
            if oldScriptName is not None:
                if __builtins__.has_key('nodescript'):
                    del __builtins__['nodescript']
        
        
    def _safeCallEnter(self):
        if self.nodeScript is not None:
            self.nodeScript.enter()
            
    def _safeCallPreDisplay(self):
        if self.nodeScript is not None:
            self.nodeScript.preDisplay()
            
    def _safeCallCameraLookAt(self):
        if self.activeNode.lookat is not None:
            self.game.getView().setCameraLookAt(self.activeNode.lookat)
        
    def _completeNodeTransition(self):
        '''
        Performs any additional final steps of the transition sequence for displaying a new node. 
        This function mainly exists in order to ensure that a cleanup function can be called when the
        transition sequence is abruptly ended by calling sequence.finish()
        '''
        self.inTransition = False
        
        if self.game.getView().getActiveNode() != self.activeNode:
            self.log.warning('The node transition sequence did not complete. Displaying node %s while having %s as active' % (self.game.getActiveNode(), self.activeNode))

        self._playMusic()
        
            
    def _playMusic(self):
        playlist = self.activeNode.musicPlaylist
        # this is necessary to combine node music with default in-game music
#        if playlist is None:
#            playlist = self.game.defaultMusicPlaylist
            
        if playlist is None:
            allLists = self.game.getResources().listResources(PanoConstants.RES_TYPE_PLAYLISTS, False)
            if allLists is not None and len(allLists) > 0:
                if self.log.isEnabledFor(logging.DEBUG):
                    self.log.debug('Randomly choosed to play playlist %s' % playlist)
                playlist = allLists[0]
            else:
                self.log.warning('No playlist found, there will be no music')
                        
        if playlist is not None:
            currentPlaylist = self.game.getMusic().getPlaylist()
            # check if already playing the same playlist
            if currentPlaylist is not None and currentPlaylist.name == playlist:
                return
            self.game.getMusic().setPlaylist(self.game.getResources().loadPlaylist(playlist)) 
            self.game.getMusic().play()
            
        
    def _persistNodescriptState(self):
        '''
        Persists the state of the current nodescript in the global persistence context.
        The variable that holds the persistent state is named as 'nodescript_' + nodescript.name.
        '''
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('persisting state for nodescript %s' % self.nodeScript.getName())
        per = self.game.getPersistence()
        nodeCtx = self.nodeScript.persistState(per)
        if nodeCtx is not None:
            globalCtx = per.getGlobal()
            globalCtx.addVar('nodescript_' + self.nodeScript.name, per.serializeContext(nodeCtx))
        
    def _restoreNodescriptState(self):
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('restoring state for nodescript %s' % self.nodeScript.name)
        per = self.game.getPersistence()
        globalCtx = per.getGlobal()
        nodeCtxStream = globalCtx.getVar('nodescript_' + self.nodeScript.name)
        if nodeCtxStream is not None:
            self.nodeScript.restoreState(per, per.deserializeContext(nodeCtxStream))
                
        
    