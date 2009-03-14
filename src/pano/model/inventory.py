import logging
import re

from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib

from constants import PanoConstants
from messaging import Messenger

class InventorySlot:
    """
    Represents a free or occupied inventory slot. A slot is free if it's item field is None.
    """
    def __init__(self, num = -1, item = None, itemCount = 0):
        self.num = num        
        self.item = item
        self.itemCount = itemCount        
        
    def isFree(self):
        return self.item is None
        
    def getNum(self):
        return self.num
    
    def setNum(self, num):
        self.num = num
        
    def getItem(self):
        return self.item
    
    def setItem(self, item):
        self.item = item
        
    def getItemCount(self):
        return self.itemCount
    
    def setItemCount(self, itemCount):
        self.itemCount = itemCount

    def __str__(self):
        return "[InventorySlot num: %i, item: %s, item_count: %i]" % (self.num, self.item, self.itemCount)

class Inventory:
    """
    Represents the player's inventory, the bag of collected items.
    This class provides just the model aspect of the inventory, for inventory rendering
    check-out the class in pano.view.inventory.InventoryView
    """
    
    def __init__(self, game, slotsCount = 10):
        self.log = logging.getLogger('pano.inventory')
        self.game = game
        self.msn = Messenger(self)
        
        # keyed by item name, contains InventoryItem instances
        self.items = {}
        self.slots = [] 
        self.setSlotsCount(slotsCount)                             
            
    def hasItem(self, itemName):
        """
        Returns True if the specified item is inside the inventory.
        """
        return self.items.has_key(itemName)
    
    def setSlotsCount(self, slotsCount):
        """
        Sets the total number of inventory slots.
        Note: This causes all slots to be recreated and become empty.
        """        
        self.slots = [] 
        for i in xrange(slotsCount):
            self.slots.append(InventorySlot(num = i))
        
    def getSlotsCount(self):
        """
        Returns the total number of inventory slots.
        """
        return len(self.slots)
    
    def getSlotByNum(self, num):
        """
        Returns the inventory slot having the given number property.
        """
        for s in self.slots:
            if s.getNum() == num:
                return s
        
        return None
    
    def getSlotByItem(self, itemName):
        """
        Returns the inventory slot that contains the given item, or None if no such slot exists.
        """
        for s in self.slots:
            if not s.isFree() and s.getItem().getName() == itemName:
                return s
    
    def setItemCount(self, itemName, count):
        """
        Sets the count of an item already in the inventory.
        For example if we want to have 5 coins we will do: inventory.setItemCount('coin', 5)
        """
        if self.hasItem(itemName):
            item = self.items[itemName]        
            item.setCount(count)
            self.msn.sendMessage(PanoConstants.EVENT_ITEM_COUNT_CHANGED, [itemName, count])
    
    def getItemCount(self, itemName):
        """
        Returns the current count for the specified item which must already be present in the inventory.
        """
        if self.hasItem(itemName):
            return self.items[itemName].getCount()
        return 0
    
    def clearItems(self):
        """
        Removes all items from the inventory.
        """
        self.items = {}
        for s in self.slots:
            s.setItem(None)
        self.msn.sendMessage(PanoConstants.EVENT_ITEMS_CLEARED)
    
    def addItem(self, itemName):
        """
        Adds an item to the inventory if it is not already there or increments the item's count 
        if it already existed in the inventory.
        """                        
#        if self.hasItem(itemName):
#            self.incrementItemCount(itemName, 1)
#        else:
        slot = self.getFreeSlot()
        if slot is not None:
            itemObj = self.game.getResources().loadItem(itemName)
            self.items[itemName] = itemObj
            self.getFreeSlot().setItem(itemObj)
            self.msn.sendMessage(PanoConstants.EVENT_ITEM_ADDED, [itemName])
        else:
            self.log.error('Could not find a free slot to add item %s' % itemName)
            
    def removeItem(self, itemName):
        """
        Removes the specified item from the inventory.
        """
        if self.hasItem(itemName):
            item = self.items[itemName]
            s = self._getSlotForItem(item)
            if s is not None:
                s.setItem(None)                        
            del self.items[itemName]
            self.msn.sendMessage(PanoConstants.EVENT_ITEM_REMOVED, [itemName])
        
    
    def incrementItemCount(self, itemName, amount):
        """
        Increments the count of the specified item by the given amount.
        Use this method to modify the item count without first querying its current count.
        """
        if self.hasItem(itemName):
            item = self.items[itemName]
            item.setCount(item.getCount() + amount)
            self.msn.sendMessage(PanoConstants.EVENT_ITEM_COUNT_CHANGED, [itemName, amount])
    
    def decrementItemCount(self, itemName, amount):
        """
        Decrements the count of the specified item by the given amount.
        Use this method to modify the item count without first querying its current count.
        """
        if self.hasItem(itemName):
            item = self.items[itemName]
            cnt = item.getCount()
            if cnt > amount:
                item.setCount(cnt - amount)
                self.msn.sendMessage(PanoConstants.EVENT_ITEM_COUNT_CHANGED, [itemName, amount])
                
    def getFreeSlot(self):
        """
        Returns the first available free slot.
        """
        for s in self.slots:
            if s.isFree():
                return s
        return None
            
    