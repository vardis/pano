
import logging

from pano.constants import PanoConstants
from pano.model.Hotspot import Hotspot
from pano.control.NodeScript import BaseNodeScript


class sudoku(BaseNodeScript):
    
    def __init__(self, game, node):
        
        # we must call the parent class
        BaseNodeScript.__init__(self, game, 'sudoku', node)
        
        self.log = logging.getLogger('sudoku')
        
        # stores the current state of the board
        self.board = []
        
        # stores the initial state of the board, as defined in start_pos.txt
        self.initBoard = []
        
        # stores the solved state of the board, as defined in solution_pos.txt
        self.solutionBoard = []
         
        
    def registerMessages(self):        
        li = [PanoConstants.EVENT_HOTSPOT_ACTION, PanoConstants.EVENT_HOTSPOT_LOOKAT]
        li.extend(BaseNodeScript.registerMessages(self))
        return li
    
        
    def enter(self):
        BaseNodeScript.enter(self)
    
        #setup the initial board
        ord0 = ord('0')
        startTxt = self.game.getResources().loadText('start_pos.txt')        
        for c in startTxt:            
            if c <= '9' and c >= '0':
                self.initBoard.append(ord(c) - ord0)
                 
        self.board.extend(self.initBoard)
                    
        #setup the solution matrix        
        solTxt = self.game.getResources().loadText('solution_pos.txt')        
        for c in solTxt:
            if c <= '9' and c >= '0':
                self.solutionBoard.append(ord(c) - ord0)
            
        self._createHotspots()
        
    
    def exit(self):
        BaseNodeScript.exit(self)
    
    
    def update(self, millis):
        BaseNodeScript.update(self, millis)
        if self.isSolutionAchieved():
            self.game.getView().getTalkBox().showText('game.success')
    
    
    def onMessage(self, msg, *args):
        if msg == PanoConstants.EVENT_HOTSPOT_ACTION:
            hotspot = args[0]
            cell = self._getCellFromName(hotspot.name)
            self.modifyCellValue(cell, 1)
            
        if msg == PanoConstants.EVENT_HOTSPOT_LOOKAT:
            hotspot = args[0]
            cell = self._getCellFromName(hotspot.name)
            self.modifyCellValue(cell, -1)
            
    
    def _getCellFromName(self, name):
        # name will be: cell_<number>
        return int(name[name.find('_') + 1:])
    
    
    def _getHotspotFromCell(self, cell):
        return self.node.getHotspot('cell_%d' % cell)
    
    
    def modifyCellValue(self, cell, amount):
        assert cell <= 81, 'cell index must be within [0, 80]'
        self.board[cell] = (self.board[cell] + amount) % 10 
        
        self.log.debug('new cell value: %d' % self.board[cell])
        
        hp = self._getHotspotFromCell(cell)
        self.game.getView().panoRenderer.replaceHotspotSprite(hp, str(self.board[cell]))
    
    
    def isSolutionAchieved(self):
        for i in xrange(81):
            if self.board[i] != self.solutionBoard[i]:
                return False
        return True        
    
    
    def _createHotspots(self):
        # for every board cell we create a hotspot
        CELL_HEIGHT = 53
        CELL_WIDTH = 53
        FAT_GRID_LINE = 7
        THIN_GRID_LINE = 3        
        
        for c in xrange(9):
            for r in xrange(9):
                n = r*9+c                
                hp = Hotspot('cell_%d' % n)
                hp.xo = c*CELL_WIDTH + FAT_GRID_LINE*(c/3) + THIN_GRID_LINE*(c % 3) + FAT_GRID_LINE - 1 
                hp.yo = (
                         r*CELL_HEIGHT + 
                         FAT_GRID_LINE*(r/3) + 
                         (3*(r/3)) + # every third row the cells have 50px height instead of 53px
                         THIN_GRID_LINE*(r % 3) + 
                         FAT_GRID_LINE - 1  # the first vertical fat line is 6px
                         )
                hp.setWidth(CELL_WIDTH)
                hp.setHeight(CELL_HEIGHT)
                hp.sprite = str(self.initBoard[n])
                hp.active = True
                
                self.node.addHotspot(hp)                
                self.game.getView().panoRenderer.renderHotspot(hp)
            
             
            