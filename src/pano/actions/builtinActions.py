from actions.BaseAction import BaseAction

BuiltinActionsNames = [    
     'acVoid',
     'acExit',
     'acPause',
     'acResume'
     ]

class VoidAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acVoid', 'Does nothing')
        
    def execute(self, game):
        BaseAction.execute(self, game)

class PauseGameAction(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, 'acPause', 'Pauses the game')
        
    def execute(self, game):
        BaseAction.execute(self, game)
#        game.getInput().pushMappings('paused')
        game.pause()
        
class ResumeGameAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self, 'acResume', 'Resumes the game')
        
    def execute(self, game):
        BaseAction.execute(self, game)
#        game.getInput().popMappings()
        game.resume()            
        
class ExitGameAction(BaseAction):
    
    def __init__(self):
        BaseAction.__init__(self, 'acExit', 'Exits the game')
        
    def execute(self, game):
        BaseAction.execute(self, game)
        game.quit()
        
                