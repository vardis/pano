from actions.BaseAction import BaseAction
from names import BuiltInActionsNames

class ExitGameAction(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, BuiltInActionsNames.ExitGameAction, 'Exits the game')
        
    def execute(self, game):
        BaseAction.execute(self, game)
        game.quit()
        