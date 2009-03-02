
class InventoryItem:
    """
    Represents an inventory item.
    For every item we define a description either in the form of simple text or as the name
    of a .sound sound which can include subtitles as well. We also define an image representation
    for the normal and selected states. Finally we can limit the number of occurrences of an item
    inside an inventory through the maxCount field which defines this upper limit.
    You define InventoryItem instances through .item data files, consult the InvetoryItemParser
    for more details.
    """
    def __init__(self, name, description = None, sound = None, image = None, selectedImage = None, count = 1, maxCount = 100):
        self.name = name    # unique name of the item
        self.sound = sound    # the sound to play for describing this item
        self.description = description  # message key for the item's description
        self.image = image  # the image to use as an icon
        self.selectedImage = selectedImage  # the image to use for drawing the icon in a selected state
        self.count = count  # the current count of this item
        self.maxCount = maxCount       # the maximum number of copies of this item in an inventory
        
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name
        
    def getSound(self):
        return self.sound
    
    def setSound(self, sound):
        self.sound = sound
        
    def getDescription(self):
        return self.description
    
    def setDescription(self, description):
        self.description = description
        
    def getImage(self):
        return self.image
    
    def setImage(self, image):
        self.image = image
        
    def getSelectedImage(self):
        return self.selectedImage
    
    def setSelectedImage(self, selectedImage):
        self.selectedImage = selectedImage    
        
    def getCount(self):
        return self.count
    
    def setCount(self, count):
        self.count = count
        
    def getMaxCount(self):
        return self.maxCount
    
    def setMaxCount(self, maxCount):
        self.maxCount = maxCount

    def __str__(self):
        return "[InventoryItem name: %s, description: %s, sound: %s, image: %s, selected_image: %s, max_count: %i]"  %  (
                                                                                                                        self.name, 
                                                                                                                        self.description, 
                                                                                                                        self.sound, 
                                                                                                                        self.image, 
                                                                                                                        self.selectedImage, 
                                                                                                                        self.maxCount)

    