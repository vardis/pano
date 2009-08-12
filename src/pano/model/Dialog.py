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


class Dialog(object):
    '''
    A dialog between two or more characters. It could also represent a monologue.
    The dialog is modelled as a hierarchical tree of options where a conversation 
    traverses the tree. 
    Customization settings include the color of each option, the associated sound
    and message key for internationalization.
    Events can be emitted when a dialog or single option is activated.
    The Dialog class is actually the Model part in the Model-View-Controller scheme
    for handling dialogs in-game. The state of a dialog is managed by the DialogState 
    which playes the role of the controller. Finally the rendering is handled by a DialogView 
    instance which is the View part. 
    '''

    def __init__(self, name):
        self.name = name
        self.options = {}
        self.initialOption = None
        self.color = [255, 255, 255]
        
        
class DialogOption(object):
    '''
    An optional dialog line which is part of a dialog tree.
    Every option has a list of sub-options which can be selected only if their parent
    option has been activated. This allows to store the options in a hierarchy.    
    '''
    def __init__(self, name, parent):
        print 'constructor of DialogOption for %s called' % name
        self.name = name
        self.parent = parent
        self.enabled = True
        self.message = None
        self.color = [255, 255, 255]
        self.sound = None
        self.events = []
        self.options = {}
        
            
        