from actions.BaseAction import BaseAction

class VoidAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'ACT_VOID', 'Does nothing')
        
    def execute(self, game):
        BaseAction.execute(self, game)
            