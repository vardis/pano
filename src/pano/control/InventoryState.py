import logging

from constants import PanoConstants
from control.fsm import FSMState

class InventoryState(FSMState):
    """
    Controls the user interaction with the inventory screen controls.
    """
    
    NAME = 'InventoryState'
    INVENTORY_MSGS = [
                PanoConstants.EVENT_ITEM_REMOVED,
                PanoConstants.EVENT_ITEM_ADDED,
                PanoConstants.EVENT_ITEM_COUNT_CHANGED,
                PanoConstants.EVENT_ITEMS_CLEARED
                ]
    
    def __init__(self, gameRef = None):
        FSMState.__init__(self, gameRef, InventoryState.NAME)
        self.log = logging.getLogger('pano.inventoryState')        
        self.activeSlot = None
        self.activeItem = None
        self.startSlot = None
        self.inventoryView = None
        
    def registerMessages(self):        
        return self.INVENTORY_MSGS                
        
    def enter(self):        
        FSMState.enter(self)                
        self.getGame().getInput().pushMappings('inventory')        
        
        self.inventoryView = self.getGame().getView().getInventoryView()
        self.inventoryView.redraw()        
        self.inventoryView.show()
        
    def exit(self):             
        FSMState.exit(self)        
        self.getGame().getInput().popMappings()
        self.inventoryView.hide()
        
    def update(self, millis):
        """
        Updates the state of the inventory.
        During an update we only need to check for the following:
            1) if a drag operation has been initiated or just ended.
            2) if the user highlights a different item, then we need to update the item description
        """
        if self.inventoryView.isVisible() and base.mouseWatcherNode.hasMouse():       
            slotNum = self.inventoryView.getSlotAtScreenPos(base.win.getPointer(0).getX(), base.win.getPointer(0).getY())            
            if slotNum is not None:            
                # if the active slot has changed, update the item description text                
                slot = self.getGame().getInventory().getSlotByNum(slotNum)                            
                if slot is not None and slot != self.activeSlot:
                    self.activeSlot = slot
                    if not slot.isFree():                        
                        self.inventoryView.setText(slot.getItem().getDescription())
                        if self.activeItem is not None:
                            self.game.getView().getMousePointer().setImageAsPointer(self.activeItem.getSelectedImage(), 0.3)
            else:
                self.activeSlot = None
                self.inventoryView.clearText()
                if self.activeItem is None:
                    self.game.getView().getMousePointer().setByName(self.inventoryView.getMousePointerName())
                else:
                    self.game.getView().getMousePointer().setImageAsPointer(self.activeItem.getImage(), 0.3)
                    
    def onMessage(self, msg, *args):                
        if msg in self.INVENTORY_MSGS and self.inventoryView is not None:
            self.log.debug('Received inventory event %s with args %s' % (msg, args[0]))
            self.inventoryView.redraw()
    
    def onInputAction(self, action):   
        self.log.debug('ACTION %s' % action) 
        if action == "item_select" and self.activeSlot is not None:
            self.log.debug('select action and activeslot is: %s' % self.activeSlot)
            if self.activeItem is None  and not self.activeSlot.isFree():
                self._setActiveItem()
            elif self.activeItem is not None  and not self.activeSlot.isFree():
                self._interactItems()
            elif self.activeItem is not None  and self.activeSlot.isFree():
                self._moveItem()    
        elif (action == "cancel" or action == "item_look") and self.activeItem is not None:
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
        self.activeItem = self.activeSlot.getItem()
        self.startSlot = self.activeSlot
        
        # change pointer to indicate the active item             
        if not self.game.getView().getMousePointer().setImageAsPointer(self.activeItem.getImage(), 0.3):
            self.log.error('Failed to set mouse pointer to selected image %s' % self.activeItem.getSelectedImage())
            
        self.log.debug('set active item to %s' % self.activeItem)
        
    def _clearActiveItem(self):
        self.activeItem = None
        self.startSlot = None
        # return pointer to normal
        self.game.getView().getMousePointer().setByName(self.inventoryView.getMousePointerName())
        
    def _interactItems(self):
        dropSlot = self.activeSlot
        if dropSlot.getNum() != self.startSlot.getNum():                    
            # broadcast message for combining the two items
            eventName = "%s-into-%s" % (self.startSlot.getItem().getName(), dropSlot.getItem().getName())
            self.log.debug("Emitting items interact event %s" % eventName)
            self.getMessenger().sendMessage(eventName)
                
        self._clearActiveItem()
    
    def _moveItem(self):
        self.activeSlot.setItem(self.activeItem)
        self.startSlot.setItem(None)        
        self._clearActiveItem()
        self.inventoryView.redraw()
        
    