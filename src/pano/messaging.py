import logging

from direct.showbase import DirectObject

class Messenger(DirectObject.DirectObject):
    """
    Objects of this class can be used for sending and receiving messages to/from
    other game components.
    """
    def __init__(self, owner):
        self.log = logging.getLogger('pano.messenger')
        self.owner = owner                
        
    def sendMessage(self, msg, args=[]):
        """
        Sends a message with the specified name and arguments.
        """
        args.insert(0, msg)
        messenger.send(msg, args)
    
    def acceptMessage(self, msg, func):
        """
        Declares that messages with the specified name should be received and handled
        by the given function.
        """
        messenger.accept(msg, self.owner, func)   
    
    def rejectMessage(self, msg):
        """
        Declares that messages with the specified name should not be received anymore. 
        """
        messenger.ignore(msg, self.owner)
    
    def rejectAll(self):
        """
        Rejects all incoming messages until a new acceptMessage call is made. 
        """
        messenger.ignoreAll(self.owner)
        