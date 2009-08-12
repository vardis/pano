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

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode

from pano.constants import PanoConstants
from pano.control.NodeScript import BaseNodeScript


class MusicExample(BaseNodeScript):
    
    def __init__(self, game, node):                
        BaseNodeScript.__init__(self, game, 'MusicExample', node)        
        self.log = logging.getLogger('MusicExample')

        # displays the current track
        self.instructions = None
        
        # used to detect a change in the active track
        self.lastActiveTrack = None
        
        # two different music playlists
        self.list1 = None
        self.list2 = None
        
        # displays active track
        self.trackLabel = None

        # displays active playlist
        self.playlistLabel = None
        
        
    def enter(self):
        BaseNodeScript.enter(self)
        
        # hold the camera fixed
        self.game.getView().getCameraController().disable()
                
        self.music = self.game.getMusic()
                
        res = self.game.getResources()
        self.list1 = res.loadPlaylist('list1')
        self.list2 = res.loadPlaylist('list2')
                
        self.music.setPlaylist(self.list1)                                
        self.music.play()            
        
        self.game.getInput().addMappings('playlist-control')    
                
                            
    def exit(self):
        BaseNodeScript.exit(self)
        self.game.getInput().removeMappings('playlist-control')
    
    
    def update(self, millis):
        BaseNodeScript.update(self, millis)
        track = self.music.getActiveTrack() # returns a tuple of the form (index, track_name, track_file)
        if self.lastActiveTrack != track:
            self.lastActiveTrack = track
            self._updateTrackLabel('[%d] %s (file: %s)' % track)
            pl = self.music.getPlaylist()
            self._updatePlaylistLabel('Current playlist: %s' % pl.name)
        
        
    def onInputAction(self, action):
        if action == "last_track":
            self.music.lastTrack()
        
        elif action == "first_track":
            self.music.firstTrack()
            
        elif action == "next_track":
            self.music.nextTrack()
        
        elif action == "previous_track":
            self.music.previousTrack()
            
        elif action == "pause_music":
            self.music.setPaused(True)
            
        elif action == "resume_music":
            self.music.setPaused(False)
            
        elif action == "volume_up":
            self.music.setVolume(self.music.getVolume() + 0.1)
            
        elif action == "volume_down":
            self.music.setVolume(self.music.getVolume() - 0.1)
            
        elif action == "next_playlist" or action == "previous_playlist":
            if self.music.getPlaylist().name == "list1":
                self.music.setPlaylist(self.list2)
            else:
                self.music.setPlaylist(self.list1)
            
        else:
            return False
        
        return True
    
        
    def _updateTrackLabel(self, s):
        if self.trackLabel:
            self.trackLabel.setText(s)
        else:
            self.trackLabel = OnscreenText(text = s,
                                         pos = (base.a2dLeft + 0.1, 0.9),
                                         align = TextNode.ALeft,
                                         scale = 0.07,
                                         fg = (1.0, 1.0, 1.0, 1.0),
                                         shadow = (0.0, 0.0, 0.0, 0.7),
                                         mayChange = True
                                         )
        
    def _updatePlaylistLabel(self, s):
        if self.playlistLabel:
            self.playlistLabel.setText(s)
        else:
            self.playlistLabel = OnscreenText(text = s,
                                             pos = (base.a2dLeft + 0.1, 0.8),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        