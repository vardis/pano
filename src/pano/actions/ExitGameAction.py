from actions.BaseAction import BaseAction

class ExitGameAction(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, 'ACT_EXIT_GAME', 'Exits the game')
        
    def execute(self, game):
        BaseAction.execute(self, game)
        game.quit()
        