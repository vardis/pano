from actions.BaseAction import BaseAction
from names import BuiltInActionsNames

class VoidAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, BuiltInActionsNames.VoidAction, 'Does nothing')
        
    def execute(self, game):
        BaseAction.execute(self, game)
            