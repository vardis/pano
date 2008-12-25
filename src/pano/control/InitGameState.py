
from pandac.PandaModules import ConfigVariableString
from pandac.PandaModules import Filename
from pandac.PandaModules import Notify
from pandac.PandaModules import MultiplexStream

from constants import PanoConstants 
from fsm import FSMState
from model.Node import Node
from model.Hotspot import Hotspot
from ExploreState import ExploreState
from resources.DirectoryResourcesLocation import DirectoryResourcesLocation 

class InitGameState(FSMState):
    def __init__(self, gameRef):
        FSMState.__init__(self, gameRef, 'InitGameState')
        self.millis = 0
        
    def setupResourcesLocations(self):

        # add the default locations
        nodesRes = DirectoryResourcesLocation(directory='data/nodes', name='nodesLoc', description='Nodes resources', resTypes=PanoConstants.RES_TYPE_NODES)
        modelsRes = DirectoryResourcesLocation(directory='data/models', name='modelsLoc', description='Models resources', resTypes=PanoConstants.RES_TYPE_MODELS)
        texturesRes = DirectoryResourcesLocation(directory='data/textures', name='texturesLoc', description='Textures resources', resTypes=PanoConstants.RES_TYPE_TEXTURES)
        fontsRes = DirectoryResourcesLocation(directory='data/fonts', name='fontsLoc', description='Fonts resources', resTypes=PanoConstants.RES_TYPE_FONTS) 
        soundsRes = DirectoryResourcesLocation(directory='data/sounds', name='soundsLoc', description='Sounds resources', resTypes=PanoConstants.RES_TYPE_SOUNDS)
        pointersRes = DirectoryResourcesLocation(directory='data/pointers', name='pointersLoc', description='Pointers resources', resTypes=PanoConstants.RES_TYPE_POINTERS)

        res = self.getGame().getResources()        
        res.addResourcesLocation(nodesRes)
        res.addResourcesLocation(modelsRes)
        res.addResourcesLocation(texturesRes)
        res.addResourcesLocation(fontsRes)
        res.addResourcesLocation(soundsRes)
        res.addResourcesLocation(pointersRes)    
        
    def enter(self):
        print 'entered initial state' 
        
		# configure resource locations
        self.setupResourcesLocations()
        
        # setup input mappings, initialise components        
        
        #enter UI mode and show the mouse
        
        # disables Panda's mouse based camera control
        base.disableMouse()
                    
        self.initialNode = Node('node1')
        
        # create a hotspot for the door exit
        exitDoor = Hotspot('exitDoor', 
                           'exits the room and ends the game',  
                           PanoConstants.CBM_FRONT_FACE, 
                           444, 444,  # x, y 
                           122, 258) # width, height
        exitDoor.setAction(self.getGame().actions().builtinNames().ExitGameAction)
        self.initialNode.addHotspot(exitDoor)
        
        self.getGame().getView().displayNode(self.initialNode)
        
        #self.game.setMouseMode(PanoConstants.MOUSE_UI_MODE)
        self.game.gameView.mousePointer.setByName(PanoConstants.SELECT_POINTER)
        
    def exit(self):
        pass            
        
    def update(self, millis):
        print 'initial state update ', millis                    
        self.millis += millis
        if self.millis > 2:
            self.getGame().getState().changeState(ExploreState.NAME)

	
