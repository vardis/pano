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

from pano.constants import PanoConstants
from pano.control.fsm import FSMState

class InventoryState(FSMState):
    """
    Controls the user interaction with the inventory screen controls.
    """
        
    INVENTORY_MSGS = [
                PanoConstants.EVENT_ITEM_REMOVED,
                PanoConstants.EVENT_ITEM_ADDED,
                PanoConstants.EVENT_ITEM_COUNT_CHANGED,
                PanoConstants.EVENT_ITEMS_CLEARED,
                PanoConstants.EVENT_ITEMS_RESTORED
                ]
    
    def __init__(self, gameRef = None):
        FSMState.__init__(self, gameRef, PanoConstants.STATE_INVENTORY)
        self.log = logging.getLogger('pano.inventoryState')                
        self.startSlot = None
        self.inventory = None
        self.inventoryView = None
        
    def registerMessages(self):        
        return self.INVENTORY_MSGS                
        
    def enter(self):        
        FSMState.enter(self)                
        self.getGame().getInput().pushMappings('inventory')        
        
        self.inventory = self.getGame().getInventory()
        
        self.inventoryView = self.getGame().getView().getInventoryView()
        self.inventoryView.redraw()
        self.inventoryView.clearText()
#        self.inventoryView.enableDebugRendering()        
        self.inventoryView.show()
        
    def exit(self):             
        FSMState.exit(self)        
        self.getGame().getInput().popMappings()
        self.inventoryView.hide()
        
    def update(self, millis):
        """
        Updates the state of the inventory.
        Currently it only checks if the user highlights a different item, then we need to update the item description
        an the mouse pointer. 
        The rules for the mouse pointer are as follows:
            a) When an item is selected, then the pointer displays the image of the item (item.getImage())
            b) When an item is already selected and the mouse hovers over an item, then the pointer displays
               the ON or selected image of the item (i.e. item.getSelectedImage())
            c) When no item is selected, then the default pointer is used (specified by the InventoryView.getMousePointerName())
        """
        if self.inventoryView.isVisible() and base.mouseWatcherNode.hasMouse():       
            slotNum = self.inventoryView.getSlotAtScreenPos(base.win.getPointer(0).getX(), base.win.getPointer(0).getY())            
            if slotNum is not None:            
                # if the active slot has changed, update the item description text                
                slot = self.inventory.getSlotByNum(slotNum)                            
                if slot is not None and slot != self.inventory.getActiveSlot():
                    self.inventory.setActiveSlot(slot)
                    if not slot.isFree():                        
                        self.inventoryView.setText(slot.getItem().getDescription())
                        if self.inventory.getActiveItem() is not None:
                            self.game.getView().getMousePointer().setImageAsPointer(self.inventory.getActiveItem().getSelectedImage(), 0.3)
                    else:
                        if self.inventory.getActiveItem() is not None:
                            self.game.getView().getMousePointer().setImageAsPointer(self.inventory.getActiveItem().getImage(), 0.3)
            else:
                self.inventory.setActiveSlot(None)
                if self.inventory.getActiveItem() is not None:
                    self.game.getView().getMousePointer().setImageAsPointer(self.inventory.getActiveItem().getImage(), 0.3)
                self.inventoryView.clearText()
                    
    def onMessage(self, msg, *args):                
        if msg in self.INVENTORY_MSGS and self.inventoryView is not None:
            self.log.debug('Received inventory event %s with args %s' % (msg, args[0]))
            self.inventoryView.redraw()
    
    def onInputAction(self, action):   
        self.log.debug('ACTION %s' % action) 
        
        if action == "item_select" and self.inventory.getActiveSlot() is not None:
            self.log.debug('select action and active slot is: %s' % self.inventory.getActiveSlot())
            
            if self.inventory.getActiveItem() is None  and not self.inventory.getActiveSlot().isFree():
                self._setActiveItem()
                
            elif self.inventory.getActiveItem() is not None  and not self.inventory.getActiveSlot().isFree():
                self._interactItems()
                
            elif self.inventory.getActiveItem() is not None  and self.inventory.getActiveSlot().isFree():
                self._moveItem()
                    
        elif (action == "cancel" or action == "item_look") and self.inventory.getActiveItem() is not None:
            self._clearActiveItem()
              
        elif action == "enable_debug":
            self.log.debug('Enabling inventory debug rendering')
            self.inventoryView.enableDebugRendering()          
            
        elif action == "disable_debug":
            self.log.debug('Disabling inventory debug rendering')
            self.inventoryView.disableDebugRendering()
        else:       
            return False
        
        return True
    
    def _setActiveItem(self):
        """
        When this is called it assumes that there is an activeSlot.
        """
        self.inventory.setActiveItem(self.inventory.getActiveSlot().getItem())
        self.startSlot = self.inventory.getActiveSlot()
        
        # change pointer to indicate the active item             
        if not self.game.getView().getMousePointer().setImageAsPointer(self.inventory.getActiveItem().getImage(), 0.3):
            self.log.error('Failed to set mouse pointer to selected image %s' % self.inventory.getActiveItem().getSelectedImage())
            
        self.log.debug('set active item to %s' % self.inventory.getActiveItem())
        
    def _clearActiveItem(self):
        self.inventory.setActiveItem(None)
        self.startSlot = None
        # return pointer to normal
        self.game.getView().getMousePointer().setByName(self.inventoryView.getMousePointerName())
        
    def _interactItems(self):
        dropSlot = self.inventory.getActiveSlot()
        if dropSlot.getNum() != self.startSlot.getNum():                    
            # broadcast message for combining the two items
            eventName = "%s-into-%s" % (self.startSlot.getItem().getName(), dropSlot.getItem().getName())
            self.log.debug("Emiting items interact event %s" % eventName)
            self.getMessenger().sendMessage(eventName)
                
        self._clearActiveItem()
    
    def _moveItem(self):
        self.inventory.getActiveSlot().setItem(self.inventory.getActiveItem())
        self.startSlot.setItem(None)        
        self._clearActiveItem()
        self.inventoryView.redraw()
        
    