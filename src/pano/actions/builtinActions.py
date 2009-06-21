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

from constants import PanoConstants
from actions.BaseAction import BaseAction
from control.InventoryState import InventoryState

BuiltinActionsNames = [    
     'acVoid',
     'acExit',
     'acPause',
     'acResume',
     'acShowConsole',
     'acToggleConsole',
     'acHideConsole',
     'acChangeState',
     'acToggleInventory',
     'acGotoNode'
     ]

def registerBultins(gameActions):    
    gameActions.registerAction(VoidAction())
    gameActions.registerAction(ExitGameAction())
    gameActions.registerAction(PauseGameAction())
    gameActions.registerAction(ResumeGameAction())
    gameActions.registerAction(ShowDebugConsoleAction())
    gameActions.registerAction(HideDebugConsoleAction())
    gameActions.registerAction(ToggleDebugConsoleAction())
    gameActions.registerAction(ToggleInventoryAction())
    gameActions.registerAction(GotoNodeAction())

class VoidAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acVoid', 'Does nothing')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)

class PauseGameAction(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, 'acPause', 'Pauses the game')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        game.pause()
        
class ResumeGameAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acResume', 'Resumes the game')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        game.resume()            

class ShowDebugConsoleAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acShowConsole', 'Show the debug console')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        if not game.isDebugConsoleVisible():
            game.showDebugConsole()
            
class ToggleDebugConsoleAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acToggleConsole', 'Toggles the debug console visibility')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        if not game.isDebugConsoleVisible():
            game.showDebugConsole()
        else:
            game.hideDebugConsole()            
        
class HideDebugConsoleAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acHideConsole', 'Hides the debug console')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        game.hideDebugConsole()        
        
class ExitGameAction(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, 'acExit', 'Exits the game')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        game.quit()
        
class ChangeState(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, 'acChangeState', 'Changes the state of the game')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        game.getState().changeState(params[0])
        
        
class ToggleInventoryAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acToggleInventory', 'Toggles the visibility of the inventory')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        if game.getState().getCurrentState().getName() == PanoConstants.STATE_INVENTORY:
            game.getState().popState()
        else:
            game.getState().pushState(PanoConstants.STATE_INVENTORY)
                            
class GotoNodeAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acGotoNode', 'Changes the currently active node.')
        
    def execute(self, game, params):
        BaseAction.execute(self, game, params)
        state = game.getState().getCurrentState() 
        if state.getName() == PanoConstants.STATE_EXPLORE:
            state.changeDisplayNode(params[0])
            