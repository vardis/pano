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
        