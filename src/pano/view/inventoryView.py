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
from pandac.PandaModules import LineSegs
from pandac.PandaModules import Vec3, VBase3 

from pano.constants import PanoConstants
from pano.util.PandaUtil import PandaUtil
from pano.resources.ResourcesTypes import ResourcesTypes
from pano.messaging import Messenger
from pano.model.inventory import Inventory
from pano.model.Sprite import Sprite


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
        self.originRelativeX, self.originRelativeY = PandaUtil.screenPointToAspect2d(0,0)
                
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
        pos, size  = PandaUtil.convertScreenToAspectCoords(self.getSlotPosSize(num))
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
        
    def enableDebugRendering(self, game):
        
        if self.debugNode is not None:
            return
        
        self.debugNode = aspect2d.attachNewNode(self.DEBUG_NODE)
                        
        w, h = PandaUtil.screenPointToAspect2d(self.slotWidth, self.slotHeight)
        w -= self.originRelativeX
        h -= self.originRelativeY
        sw, sh = PandaUtil.screenPointToAspect2d(self.offsetX, self.offsetY)
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
#        self.debugNode.node().removeAllChildren()
#        self.debugNode.removeNode()
        self.debugNode.detachNode()
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
    
    ButtonStateNormal = 1
    ButtonStatePressed = 2
    ButtonStateHover = 3
    
    POINTER_NAME = "inventory_pointer"
    INVENTORY_SCENE_NODE = "inventory_sceneNode"
    ICONS_NODE = "inventory_icons_node"
    BACKDROP_NODE = "backdrop"
    TEXT_NODE = "item_text"
    
    
    def __init__(self, game):
        self.log = logging.getLogger('pano.inventoryView')
        self.game = game
        self.msn = Messenger(self)  # the messenger is used to broadcast user events related to the interface 
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
        
        # scrolling and paging buttons are DirectButton instances          
        self.nextPageButton        = None
        self.prevPageButton        = None        
        self.scrollNextButton      = None
        self.scrollPrevButton      = None
        
        # specifies the range of items to be rendered in the next frame as a list [start_item_index, end_item_index]
        # used for scrolling and paging
        self.itemsRange = None
        
        # number of items displayed per page
        self.pageSize = 0
        
        # provides the layout of the slots
        self.slotsLayout = None     
        
        # stores image objects for each item's icon
        self.itemIcons = []
        
        self.mousePointer = InventoryView.POINTER_NAME
        
        self.debugLayout = False        
        

    def initialize(self, inventory):
        """
        Initialises the inventory, call this method only once otherwise resources could be leaked
        and rendering artifacts created.
        """
        if self.node is not None:
            self.node.removeNode()
#            self.node.detachNode()
            
        self.node      = aspect2d.attachNewNode(InventoryView.INVENTORY_SCENE_NODE)
        self.iconsNode = self.node.attachNewNode(InventoryView.ICONS_NODE)
        
        # from here on we just initialize the member fields according to the cvars...
        cfg = self.game.getConfig()
        if not self._validateConfig(cfg):
            self.log.error('Missing or invalid inventory configuration')
            return
        
        view = self.game.getView()
        
        if self.backdropImageObject is not None:
            self.backdropImageObject.destroy()
            self.backdropImageObject = None        
        
        self.pos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_POS)
        if self.pos is None:
            self.pos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_REL_POS)
            self.pos = view.relativeToAbsolute(self.pos)
                                
        self.textPos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_TEXT_POS)
        if self.textPos is None:
            self.textPos = cfg.getVec2(PanoConstants.CVAR_INVENTORY_REL_POS)
            self.textPos = view.relativeToAbsolute(self.textPos)
                                
        self.pos, self.textPos = PandaUtil.convertScreenToAspectCoords([self.pos, self.textPos])
        
            
        self.size = cfg.getVec2(PanoConstants.CVAR_INVENTORY_SIZE, (1.0, 1.0))
            
        self.textScale = cfg.getFloat(PanoConstants.CVAR_INVENTORY_TEXT_SCALE, 0.07)
        self.opacity   = cfg.getFloat(PanoConstants.CVAR_INVENTORY_OPACITY)
        self.fontName  = cfg.get(PanoConstants.CVAR_INVENTORY_FONT)
        self.fontColor = cfg.getVec4(PanoConstants.CVAR_INVENTORY_FONT_COLOR)
        if self.fontColor is None:
            self.fontColor = (1.0, 1.0, 1.0, 1.0)
            
        self.fontBgColor = cfg.getVec4(PanoConstants.CVAR_INVENTORY_FONT_BG_COLOR)
        if self.fontBgColor is None:
            self.fontBgColor = (0.0, 0.0, 0.0, 0.0)
            
        self.mousePointer = cfg.get(PanoConstants.CVAR_INVENTORY_POINTER)
                
        layout = cfg.get(PanoConstants.CVAR_INVENTORY_SLOTS)                    
        self._parseLayout(layout)
        
        slotsCount = self.slotsLayout.getNumSlots()
        self.log.debug('Setting slots count to %i' % slotsCount)
        
        # by default render all items, the controller state can later overridde this
        self.itemsRange = [0, slotsCount]
        
        if cfg.hasVar(PanoConstants.CVAR_INVENTORY_PAGESIZE):
            self.pageSize = cfg.getInt(PanoConstants.CVAR_INVENTORY_PAGESIZE)
        else:
            self.pageSize = slotsCount
        
        self.inventory = inventory
        self.inventory.setSlotsCount(slotsCount)   
        
        self.backdropImage = cfg.get(PanoConstants.CVAR_INVENTORY_BACKDROP)    
        if self.backdropImage is not None:         
            self._createBackdrop(show = False)
            
        # create the scrolling and paging gui buttons            
        self._createButtons(cfg)
                
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
        if self.nextPageButton:
            self.nextPageButton.show()
            
        if self.prevPageButton:
            self.prevPageButton.show()
            
        if self.scrollNextButton:
            self.scrollNextButton.show()
            
        if self.scrollPrevButton:
            self.scrollPrevButton.show()
            
        if self.debugLayout:
            self.enableDebugRendering()        
    
    
    def hide(self):
        """
        Hides the inventory.
        """
        self.node.hide()
        if self.nextPageButton:
            self.nextPageButton.hide()
            
        if self.prevPageButton:
            self.prevPageButton.hide()
        
        if self.scrollNextButton:
            self.scrollNextButton.hide()
            
        if self.scrollPrevButton:
            self.scrollPrevButton.hide()
            
        if self.debugLayout:
            self.disableDebugRendering()
    
    
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
        self.slotsLayout.enableDebugRendering(self.game)
        self.debugLayout = True
        
    def disableDebugRendering(self):
        self.slotsLayout.disableDebugRendering(self.game)
        self.debugLayout = False            
    
    def _validateConfig(self, config):        
        return (config.hasVar(PanoConstants.CVAR_INVENTORY_BACKDROP) 
            and (config.hasVar(PanoConstants.CVAR_INVENTORY_POS) or config.hasVar(PanoConstants.CVAR_INVENTORY_REL_POS))
            and (config.hasVar(PanoConstants.CVAR_INVENTORY_TEXT_POS) or config.hasVar(PanoConstants.CVAR_INVENTORY_REL_POS))
            and config.hasVar(PanoConstants.CVAR_INVENTORY_SIZE)
            and config.hasVar(PanoConstants.CVAR_INVENTORY_FONT)
            and config.hasVar(PanoConstants.CVAR_INVENTORY_POINTER)
            and config.hasVar(PanoConstants.CVAR_INVENTORY_SLOTS))
    
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
            sort = 0)
        
        self.backdropImageObject.setTransparency(TransparencyAttrib.MAlpha)
        self.backdropImageObject.setBin("fixed", PanoConstants.RENDER_ORDER_INVENTORY)
        
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
             text=translated, 
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
        self.itemText.setBin("fixed", PanoConstants.RENDER_ORDER_INVENTORY_ITEMS)
    
    
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
        
        startItem = 0
        endItem = self.inventory.getSlotsCount()
        if self.itemsRange is not None:
            startItem = self.itemsRange[0]
            endItem = self.itemsRange[1]
            
        for i in xrange(endItem - startItem):
            itemNum = startItem + i
            s = self.inventory.getSlotByNum(itemNum)
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
                iconNode.setBin("fixed", PanoConstants.RENDER_ORDER_INVENTORY_ITEMS)
                self.itemIcons.append(iconNode)
                
    
    def _createButtons(self, cfg):
        '''
        Creates DirectGui elements for displaying the paging and scrolling buttons.
        The sprite names are read from the configuration.
        The create DirectButtons use sprites as images.
        @param cfg: a ConfigVars instance
        '''
        # button to display next page of items
        nxPgBtnSprite        = cfg.get(PanoConstants.CVAR_INVENTORY_NEXTPAGE_SPRITE)
        nxPgBtnPressedSprite = cfg.get(PanoConstants.CVAR_INVENTORY_NEXTPAGE_PRESSED_SPRITE)
        nxPgBtnHoverSprite   = cfg.get(PanoConstants.CVAR_INVENTORY_NEXTPAGE_HOVER_SPRITE)
        nxPgBtnPos           = cfg.getVec2(PanoConstants.CVAR_INVENTORY_NEXTPAGE_POS)
                
        # button to display previous page of items
        pvPgBtnSprite        = cfg.get(PanoConstants.CVAR_INVENTORY_PREVPAGE_SPRITE)
        pvPgBtnPressedSprite = cfg.get(PanoConstants.CVAR_INVENTORY_PREVPAGE_PRESSED_SPRITE)
        pvPgBtnHoverSprite   = cfg.get(PanoConstants.CVAR_INVENTORY_PREVPAGE_HOVER_SPRITE)
        pvPgBtnPos           = cfg.getVec2(PanoConstants.CVAR_INVENTORY_PREVPAGE_POS)
        
        # button to scroll to next items 
        scrNxBtnSprite        = cfg.get(PanoConstants.CVAR_INVENTORY_SCROLLNEXT_SPRITE)
        scrNxBtnPressedSprite = cfg.get(PanoConstants.CVAR_INVENTORY_SCROLLNEXT_PRESSED_SPRITE)
        scrNxBtnHoverSprite   = cfg.get(PanoConstants.CVAR_INVENTORY_SCROLLNEXT_HOVER_SPRITE)
        scrNxBtnPos           = cfg.getVec2(PanoConstants.CVAR_INVENTORY_SCROLLNEXT_POS)
        
        # button to scroll to previous items 
        scrPvBtnSprite        = cfg.get(PanoConstants.CVAR_INVENTORY_SCROLLPREV_SPRITE)
        scrPvBtnPressedSprite = cfg.get(PanoConstants.CVAR_INVENTORY_SCROLLPREV_PRESSED_SPRITE)
        scrPvBtnHoverSprite   = cfg.get(PanoConstants.CVAR_INVENTORY_SCROLLPREV_HOVER_SPRITE)
        scrPvBtnPos           = cfg.getVec2(PanoConstants.CVAR_INVENTORY_SCROLLPREV_POS)
                
        sprites = self.game.getView().getSpritesFactory() 
        origin = aspect2d.getRelativePoint(screen2d, VBase3(0, 0, 0))
                        
        # for every button define property name, position, callback, list of sprites for normal, pressed and hover state
        pagingButtons = [
                         ('nextPageButton', nxPgBtnPos, self._nextPageCallback, 
                                                           [
                                                           (nxPgBtnSprite, 'next_page_sprite'), 
                                                           (nxPgBtnPressedSprite,'next_page_pressed_sprite'), 
                                                           (nxPgBtnHoverSprite,'next_page_hover_sprite')
                                                           ]), 
                         ('prevPageButton', pvPgBtnPos, self._previousPageCallback, 
                                                           [
                                                           (pvPgBtnSprite, 'previous_page_sprite'), 
                                                           (pvPgBtnPressedSprite,'previous_page_pressed_sprite'), 
                                                           (pvPgBtnHoverSprite,'previous_page_hover_sprite')
                                                           ]),
                        ('scrollNextButton', scrNxBtnPos, self._scrollNextCallback, 
                                                           [
                                                           (scrNxBtnSprite, 'scroll_next_sprite'), 
                                                           (scrNxBtnPressedSprite,'scroll_next_pressed_sprite'), 
                                                           (scrNxBtnHoverSprite,'scroll_next_hover_sprite')
                                                           ]),
                        ('scrollPrevButton', scrPvBtnPos, self._scrollPreviousCallback, 
                                                           [
                                                           (scrPvBtnSprite, 'scroll_previous_sprite'), 
                                                           (scrPvBtnPressedSprite,'scroll_previous_pressed_sprite'), 
                                                           (scrPvBtnHoverSprite,'scroll_previous_hover_sprite')
                                                           ]),
                         ]
        
        
        for buttonName, buttonPos, buttonCallback, spritesList in pagingButtons:
            buttonGeoms = [None, None, None, None]            
            btnScrBounds = [0,0,0]
            i = 0
            for spriteFile, spriteName in spritesList:
                print 'adding sprite %s' % spriteName
                if spriteFile is not None:
                    spr = None
                    if spriteFile.rindex('.') >= 0:
                        ext = spriteFile[spriteFile.rindex('.'):]
                        print ext
                        if ResourcesTypes.isExtensionOfType(ext, PanoConstants.RES_TYPE_IMAGES):
                            spr = Sprite(spriteName)
                            spr.image = spriteFile
                    else:
                        spr = self.game.getResources().loadSprite(spriteFile)
                    
                    if spr:
                        buttonGeoms[i] = sprites.createSprite(spr).nodepath
                        buttonGeoms[i].setScale(1.0)
                        btnScrBounds = aspect2d.getRelativePoint(screen2d, VBase3(spr.width, 1.0, spr.height)) - origin
                        btnScrBounds[2] *= -1
                    
                i += 1
    
            if buttonGeoms[0] is not None:
                b = DirectButton(geom = (
                                         buttonGeoms[0], 
                                         buttonGeoms[1] if buttonGeoms[1] else buttonGeoms[0], 
                                         buttonGeoms[2] if buttonGeoms[2] else buttonGeoms[0], 
                                         buttonGeoms[3] if buttonGeoms[3] else buttonGeoms[0]), 
                                         relief=None)
                b['geom_pos'] = (0,0,0)
                b.setTransparency(1)
                
                # if position is omitted from the configuration, put the button on the upper left corner
                if buttonPos is not None:
                    b.setPos(aspect2d.getRelativePoint(screen2d, VBase3(buttonPos[0], 1.0, buttonPos[1])))
                else:
                    b.setPos(origin[0], 1.0, origin[2])
                    
                b.setScale(btnScrBounds[0], 1.0, btnScrBounds[2])
                b.setFrameSize((0, btnScrBounds[0], 1.0, btnScrBounds[2]))
                b['command'] = buttonCallback
                b['extraArgs'] = (self.msn,)
                b.hide()
            else:
                b = None
            
            setattr(self, buttonName, b)
            
            
    def _nextPageCallback(self, messenger):
        '''
        Callback for next page button which only sends the appropriate message.
        '''
        messenger.sendMessage(PanoConstants.EVENT_ITEMS_NEXT_PAGE)
    
    def _previousPageCallback(self, messenger):
        messenger.sendMessage(PanoConstants.EVENT_ITEMS_PREV_PAGE)
            
    def _scrollNextCallback(self, messenger):        
        messenger.sendMessage(PanoConstants.EVENT_ITEMS_SCROLL_NEXT)
    
    def _scrollPreviousCallback(self, messenger):
        messenger.sendMessage(PanoConstants.EVENT_ITEMS_SCROLL_PREV)
        
    