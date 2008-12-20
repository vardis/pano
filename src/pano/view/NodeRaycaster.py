from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import CollisionHandlerQueue
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import GeomNode

class NodeRaycaster:
    def __init__(self, renderer):
        self.renderer = renderer
        
        #Stores the collisions of the camera ray with the cubemap
        self.collisionsQueue = None
        
        #Variables for setting up collision detection in Panda
        self.pickerNP = None
        self.pickerNode = None
        self.pickerRay = None
        self.traverser = None
        
    def initialise(self):
        """
        To setup collision detection we need:
            a. A CollisionNode having a ray as its solid and placed at the position
               of the camera while also having the same orientation as the camera.
            b. A new nodepath placed in the scenegraph as an immediate child of the
               camera. It will be used to insert the collision node in the scenegraph.
            c. A CollisionRay for firing rays based on mouse clicks.
            d. A collisions traverser.
            e. A collisions queue where all found collisions will be stored for later
               processing.
        """
        self.traverser = CollisionTraverser('Hotspots collision traverser')
        base.cTrav = self.traverser    
        
        self.collisionsQueue = CollisionHandlerQueue()
        
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
    
        self.pickerRay=CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)    
        
        self.pickerNP = base.camera.attachNewNode(self.pickerNode)
        self.traverser.addCollider(self.pickerNP, self.collisionsQueue)
        
    def raycastMouse(self, mouseX, mouseY):
        '''
        Raycasts a camera ray against the rendered node and returns information
        regarding the hit point, if any.
        
        Returns: The face code and the x, y coordinates in the image space of the face. 
        '''        
        #This makes the ray's origin the camera and makes the ray point 
        #to the screen coordinates of the mouse
        self.pickerRay.setFromLens(base.camNode, mouseX, mouseY)
        
        #Check for collision only with the cubemap
        self.traverser.traverse(self.renderer.nodepath())
        if self.collisionsQueue.getNumEntries() > 0:
            self.collisionsQueue.sortEntries()
            cEntry = self.collisionsQueue.getEntry(0)
            
            print cEntry
            
            #We have the point and normal of the collision
            p = cEntry.getSurfacePoint(render)
            n = cEntry.getSurfaceNormal(render)
            print p, n
            
            face = self.renderer.findFaceFromNormal(n)
            print face
            
            # get the coordinates of the hit point in the local coordinate
            # system of the respective cubemap face
            x, y = self.renderer.getFaceLocalCoords(face, p)
            print x, y
            
            return face, x, y
            