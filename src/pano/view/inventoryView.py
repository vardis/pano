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
import re

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import DirectButton
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import TextNode, NodePath

from constants import PanoConstants
from model.inventory import Inventory

class SlotsLayout:
    """
    Defines the operations for slots providers, i.e. objects that provide a collection of InventorySlot
    objects where items are place and manages their positioning and sizing.    
    """    
        
    def getSlots(self):
        """
        Returns the collection of InventorySlot objects.
        """
        return None
        
    def getNumSlots(self):
        """
        Returns the total number of slots available on screen.
        """
        return 0        
    
    def getFreeSlot(self):
        """
        Returns a slot that is empty or None if all slots are occupied by items.
        """
        return None
    
    def getSlotPosSize(self, num):
        """
        Returns two tuples of floats containing the position and dimensions of the num_th slot in screen space (i.e. pixels).
        """
        return (0.0, 0.0, 0.0), (1.0, 1.0, 1.0) 
    
    def getRelativeSlotPosSize(self, num):
        """
        Returns two tuples of floats containing the position and dimensions of the num_th slot in aspect2d space.
        """
        return (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
        
    def getSlotAtScreenPos(self, x, y):
        """
        Returns the number of slot that contains the point (x, y).
        """
        return None
    
    def enableDebugRendring(self, game):
        """
        Called when the layout should render some debug info.
        """
        pass
    
    def disableDebugRendring(self, game):
        """
        Called when the layout should stop rendering debug info.
        """
        pass
    
from pandac.PandaModules import LineSegs 

class GridSlotsLayout(SlotsLayout):
    """
    Defines a grid layout for positioning the inventory's slots on screen.
    You can define the origin of the grid (the top left point), the grid's
    resolution, the size of each slot and the offset between slots.
    """
    
    DEBUG_NODE = "inventory_debug_node"
    
    def __init__(self, game, pos, res, size, offset):
        self.log = logging.getLogger('gridlayout')
        self.game = game
        self.pos = pos
        self.resX = res[0]
        self.resY = res[1]
        self.slotWidth = size[0]
        self.slotHeight = size[1]
        self.offsetX = offset[0]
        self.offsetY = offset[1]
        self.gridWidth = res[0] * size[0] + (res[0] - 1) * offset[0]
        self.gridHeight = res[1] * size[1] + (res[1] - 1) * offset[1]
        self.slotsLayout = []
        self.debugNode = None   # parent of all debug renderings
        
        for i in xrange(self.getNumSlots()):
            s_pos_x = (i % self.resY) * (self.slotWidth + self.offsetX) + self.pos[0] 
            s_pos_y = (i / self.resY) * (self.slotHeight + self.offsetY) + self.pos[1]
            self.slotsLayout.append(((s_pos_x, s_pos_y), (self.slotWidth, self.slotHeight)))
        
        # get the origins aspect coordinates, we need this in order to transform lengths    
        self.originRelativeX, self.originRelativeY = self.game.getView().convertScreenToAspectCoords([(0,0)])[0]
                
    def drawBorder(self, bounds,color):
        LS=LineSegs()
        LS.setColor(*color)
        LS.moveTo(bounds[0],0,bounds[2])
        LS.drawTo(bounds[0],0,bounds[3])
        LS.drawTo(bounds[1],0,bounds[3])
        LS.drawTo(bounds[1],0,bounds[2])
        LS.drawTo(bounds[0],0,bounds[2])
        return LS.create() 
        
    def getNumSlots(self):
        return self.resX * self.resY
    
    def getSlotPosSize(self, num):
        if num >= len(self.slotsLayout):
            raise IndexError("Passed num value %i is not less than the limit of %i slots" % (num, len(self.slotsLayout)))        
        else:
            return self.slotsLayout[num] 
        
    def getRelativeSlotPosSize(self, num):                
        pos, size  = self.game.getView().convertScreenToAspectCoords(self.getSlotPosSize(num))
        return (pos, (size[0] - self.originRelativeX, size[1] - self.originRelativeY))
        
    def getSlotAtScreenPos(self, x, y):
        # first check for points that are outside of the grid's bounds 
        if x < self.pos[0] or x > (self.gridWidth + self.pos[0]):
            return None
        
        if y < self.pos[1] or y > (self.gridHeight + self.pos[1]):
            return None
        
        xg, yg = x - self.pos[0], y - self.pos[1]
        stepX = self.slotWidth + self.offsetX
        stepY = self.slotHeight + self.offsetY
        
        # next check if x, y is within a slot's bounds or lies between two slots
        if ((xg % stepX) < self.slotWidth) and ((yg % stepY) < self.slotHeight):
            # we are inside a slot, find its number
            xnum = int(xg / stepX)
            ynum = int(yg / stepY)
            return ynum * self.resX + xnum
        else:
            return None
        
    def enableDebugRendring(self, game):
        
        if self.debugNode is not None:
            return
        
        self.debugNode = aspect2d.attachNewNode(self.DEBUG_NODE)
                        
        w, h = game.getView().convertScreenToAspectCoords([(self.slotWidth, self.slotHeight)])[0]
        w -= self.originRelativeX
        h -= self.originRelativeY
        sw, sh = game.getView().convertScreenToAspectCoords([(self.offsetX, self.offsetY)])[0]
        sw -= self.originRelativeX
        sh -= self.originRelativeY
        
        for i in xrange(self.getNumSlots()):
            pos, size = self.getRelativeSlotPosSize(i)
          
            x,z = pos
            self.log.debug('i=%i aspect_pos(%f, %f) frame(%f,%f,%f,%f)' % (i, x, z, x, x+w, z, z+h))
            node = self.drawBorder((x, x+w, z, z+h), (0,1,0,1))
            np = NodePath(node)
            np.reparentTo(self.debugNode) 
                        
            h_offnode = self.drawBorder((x+w, x+w+sw, z, z+h), (1,0,0,1))
            h_offnp = NodePath(h_offnode)
            h_offnp.reparentTo(self.debugNode)
            
            v_offnode = self.drawBorder((x, x+w, z+h, z+h+sh), (0,0,1,1))
            v_offnp = NodePath(v_offnode)
            v_offnp.reparentTo(self.debugNode)
            
    def disableDebugRendering(self, game):
        self.debugNode.node().removeAllChildren()
        self.debugNode.removeNode()
        self.debugNode = None
    
class ImageBasedSlotsLayout(SlotsLayout):
    """
    This type of provider uses an image and its non-black regions to determine  the areas that slots occupy.
    A flood-fill algorithm discovers the rectangle bounds that covers these regions and assigns these bounds 
    to the respective slot.    
    """
    pass

class GenericSlotsLayout(SlotsLayout):
    """
    This type of provider uses a programming interface for declaring the slots along with their attributes. 
    """
    def addSlot(self, slot):
        pass
    
    def removeSlot(self, slot):
        pass

class InventoryView:
    """
    Renders the inventory screen.
    """
    
    POINTER_NAME = "inventory_pointer"
    INVENTORY_SCENE_NODE = "inventory_sceneNode"
    ICONS_NODE = "inventory_icons_node"
    BACKDROP_NODE = "backdrop"
    TEXT_NODE = "item_text"
    
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.inventoryView')
        self.game = game
        self.inventory = None   # the inventory to render
        
        self.node = None           # the root scenegraph node for inventory rendering nodes
        self.iconsNode = None      # the parent node for all OnscreenImages that render items' icons
        self.pos = (0.0, 0.0)      # position in absolute screen coordinates
        self.size = (1.0, 1.0)     # size in absolute screen coordinates
        self.textPos = (0.0, 0.0)   # position of the item's description text
        self.textScale = 0.07       # the text scale
        self.opacity = 1.0         # controls the opacity of all rendering elements included in the inventory
        
        self.backdropImage = None        # the name of the image to use as a backdrop
        self.backdropImageObject = None  # the OnscreenImage object used to render the backdrop
        self.backdropNode = None         # the scenegraph node that parents the backdrop

        self.updateIcons = False        # if True then we need to update the rendering of the items' icons
        self.itemText = None        # the TextNode used to render the text
        self.itemTextNode = None    # nodepath that acts as a parent to the TextNode
        self.fontName = None        # the name of the font to use when rendering items' descriptions
        self.font = None            # the Panda3D font resource
        self.fontColor = (1.0, 1.0, 1.0, 1.0)    # colour of the text for an item's description      
        self.fontBgColor = (0.0, 0.0, 0.0, 1.0)  # background colour of the text
        
        # provides the layout of the slots
        self.slotsLayout = None     
        
        # stores image objects for each item's icon
        self.itemIcons = []
        
        self.mousePointer = InventoryView.POINTER_NAME        

    def initialize(self, inventory):
        """
        Initialises the inventory, call this method only once otherwise resources could be leaked
        and rendering artifacts created.
        """
        if self.node is not None:
            self.node.removeNode()
        self.node = aspect2d.attachNewNode(InventoryView.INVENTORY_SCENE_NODE)
        self.iconsNode = self.node.attachNewNode(InventoryView.ICONS_NODE)
        
        cfg = self.game.getConfig()             
        view = self.game.getView()
        
        if self.backdropImageObject is not None:
            self.backdropImageObject.destroy()
        self.backdropImage = cfg.get(PanoConstants.CVAR_INVENTORY_BACKDROP)
        
        self.pos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_POS)
        if self.pos is None:
            self.pos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_REL_POS)
            self.pos = view.relativeToAbsolute(self.pos)
                                
        self.textPos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_TEXT_POS)
        if self.textPos is None:
            self.textPos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_REL_POS)
            self.textPos = view.relativeToAbsolute(self.textPos)
                        
        self.pos, self.textPos = view.convertScreenToAspectCoords([self.pos, self.textPos])
            
        self.size = cfg.getVec2(PanoConstants.CVAR_INVENTORY_SIZE, (1.0, 1.0))
            
        self.textScale = cfg.getFloat(PanoConstants.CVAR_INVENTORY_TEXT_SCALE, 0.07)
        self.opacity = cfg.getFloat(PanoConstants.CVAR_INVENTORY_OPACITY)
        self.fontName = cfg.get(PanoConstants.CVAR_INVENTORY_FONT)
        self.fontColor = cfg.getVec4(PanoConstants.CVAR_INVENTORY_FONT_COLOR)
        self.fontBgColor = cfg.getVec4(PanoConstants.CVAR_INVENTORY_FONT_BG_COLOR)
        self.mousePointer = cfg.get(PanoConstants.CVAR_INVENTORY_POINTER)
        
        layout = cfg.get(PanoConstants.CVAR_INVENTORY_SLOTS)                
        self._parseLayout(layout)            
        self._createBackdrop(show = False)
        
        self.inventory = inventory
        slotsCount = self.slotsLayout.getNumSlots()
        self.log.debug('Set slots count to %i' % slotsCount)
        self.inventory.setSlotsCount(slotsCount)
        
        # force an initial rendering of the icons
        self.updateIcons = True
        
        # start as  hidden
        self.node.hide()
        
    def update(self, millis):
        """
        Re-renders anything that has updated.        
        """
        if self.isVisible() and self.updateIcons:
            self._renderItemsIcons()
            self.updateIcons = False
            
    def redraw(self):
        """
        Called to indicate that the underlying inventory has updated its state and now we
        should redraw it.
        """
        self.updateIcons = True                
        
    def show(self):
        """
        Shows the inventory.
        """
        self.node.show()        
    
    def hide(self):
        """
        Hides the inventory.
        """
        self.node.hide()
    
    def isVisible(self):
        """
        Returns True if the inventory is visible and False if otherwise.
        """
        return (self.node is not None) and (not self.node.isHidden())
    
    def getMousePointerName(self):
        return self.mousePointer
    
    def getSlotAtScreenPos(self, x, y):
        return self.slotsLayout.getSlotAtScreenPos(x, y)
        
    def getBackdropImage(self):
        return self.backdropImage
    
    def setBackdropImage(self, imageName):
        self.backdropImage = imageName
        self._createBackdrop()    
        
    def getText(self):
        return self.text
    
    def setText(self, text):
        self.text = text
        self._updateText()
        
    def clearText(self):
        self.text = ""
        if self.itemTextNode is not None:
            self.itemTextNode.hide()            
        
    def getNode(self):
        return self.node
    
    def enableDebugRendering(self):
        self.slotsLayout.enableDebugRendring(self.game)
        
    def disableDebugRendering(self):
        self.slotsLayout.disableDebugRendering(self.game)            
    
    def _createBackdrop(self, show = True):
        """
        Setups rendering for the inventory's backdrop image.
        The backdrop image is rendered through a OnscreenImage object and is attached under the scenegraph node
        named Inventory.BACKDROP_NODE.
        If the parameter show is True then the backdrop image becomes visible as well, otherwise it is hidden.
        """
        if self.backdropImageObject is not None:
            self.backdropImageObject.destroy()
            self.backdropImageObject = None
        
        if self.backdropNode is not None:
            self.backdropNode.removeNode()
            
        imagePath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, self.backdropImage)        
            
        self.backdropNode = self.node.attachNewNode(InventoryView.BACKDROP_NODE)        
        self.backdropImageObject = OnscreenImage(
            parent = self.node,
            image = imagePath, 
            pos = (self.pos[0], 0.0, self.pos[1]), 
#            scale= (self.size[0], 1.0, self.size[1]),
            sort = 0)
        self.backdropImageObject.setTransparency(TransparencyAttrib.MAlpha)
        self.backdropImageObject.setBin("fixed", 41)
        
        if not show:
            self.backdropNode.hide()
        
        
    def _updateText(self):     
        if self.itemText is not None:
            self.itemText.destroy()
            self.itemText = None
                   
        if self.itemTextNode is None:            
            self.itemTextNode = self.node.attachNewNode(self.TEXT_NODE)
            self.itemTextNode.setPos(self.textPos[0], 0.0, self.textPos[1])
        self.itemTextNode.show()
            
        i18n = self.game.getI18n()        
        translated = i18n.translate(self.text)
        
        localizedFont = i18n.getLocalizedFont(self.fontName)
        fontPath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_FONTS, localizedFont)                                    
        self.font = loader.loadFont(fontPath)
        
        self.itemText = DirectButton(
             parent=self.itemTextNode,
             text=translated + ' x30', 
             text_font=self.font,
             text_bg=(self.fontBgColor[0], self.fontBgColor[1], self.fontBgColor[2], self.fontBgColor[3]),
             text_fg=(self.fontColor[0], self.fontColor[1], self.fontColor[2], self.fontColor[3]),
             text_scale=self.textScale, 
             frameColor=(0,0,0,0),
             text_wordwrap=None,
             text_align = TextNode.ALeft,
             sortOrder = 10,
             pressEffect=0
             )
        self.itemText.setBin("fixed", 45)
    
    def _parseLayout(self, layoutName):
        layoutName = layoutName.strip()
        if layoutName.startswith('grid'):
            # pos, res, size, offset
            grid_re = re.compile(r'grid\(\s*(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+')
            m = grid_re.match(layoutName)
            self.slotsLayout = GridSlotsLayout(self.game, (int(m.group(1)) + self.pos[0], int(m.group(2)) + self.pos[1]),  # position within inventory
                                                   (int(m.group(3)), int(m.group(4))),  # grid resolution
                                                   (int(m.group(5)), int(m.group(6))),  # slot size
                                                   (int(m.group(7)), int(m.group(8))))  # slots offset
        elif layoutName.starts_with('image'):
            self.slotsLayout = ImageBasedSlotsProvider(layoutName)
        # a default to avoid None
        else:
            self.slotsLayout = GridSlotsLayout(self.game, 100, 100, 5, 5, 50, 50)
            
    def _renderItemsIcons(self):
        
        self.iconsNode.node().removeAllChildren()
        for icon in self.itemIcons:
            icon.destroy()
        self.itemIcons = []
        
        for i in xrange(self.inventory.getSlotsCount()):
            s = self.inventory.getSlotByNum(i)
            if not s.isFree():
                # get slot position and size in aspect2d space
                p, sz = self.slotsLayout.getRelativeSlotPosSize(s.getNum())
                itemImage = s.getItem().getImage()
                imagePath = self.game.getResources().getResourceFullPath(PanoConstants.RES_TYPE_TEXTURES, itemImage)
                iconNode = OnscreenImage(
                                         parent=self.iconsNode, 
                                         image=imagePath, 
                                         pos=(p[0] + sz[0]/2.0, 0.0, p[1]+sz[1]/2.0),
                                         scale=0.2                                      
                                         )
                iconNode.setTransparency(TransparencyAttrib.MAlpha)
                iconNode.setBin("fixed", 45)
                self.itemIcons.append(iconNode)
                
                    
    