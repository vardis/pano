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
from direct.interval.MetaInterval import Sequence
from direct.interval.LerpInterval import LerpColorScaleInterval
from pandac.PandaModules import TextNode

from pano.control.NodeScript import BaseNodeScript


class example_sounds(BaseNodeScript):
    '''
    Gives an example of how to play and manage sounds. 
    
    The code below runs as the managing script of the example_sounds node which is defined in example_sounds.node .
    Such managing scripts are termed NodeScript and are essentially an FSM linked with a node for the purpose of
    managing its state. Nodescripts are optional though, nodes can be defined without a nodescript.
    
    Being state machines in nature, you will methods such as 'enter', 'exit' and 'update'. The 'enter' method
    will be called only once, at the time the node becomes active. Likewise 'exit' will be called only once, when
    the node becomes inactive. On the other hand 'update' will be invoked with the game logic update, so many times
    per second.         
    '''

    def __init__(self, game, node):
        BaseNodeScript.__init__(self, game, 'SoundsExample', node)
        self.log = logging.getLogger('SoundsExample')
        
        # reference to sounds fx player
        self.sounds = None
        
        # the following set of fields are UI labels
        self.instructions = None
        self.soundsStatusText = None
        self.volumeText = None
        self.rateText = None
        self.balanceText = None
        self.loopText = None
        self.eventText = None
        
        # reference to the 'blah' sound 
        self.blahSound = None
        
        # holds the status of sounds, if True then sounds are globally enabled
        self.lastStatus = True
        
        # flags that indicate if the respective property has been update by the user
        self.updateVolume = False
        self.updateRate = False
        self.updateBalance = False
        self.updateLooping = False
        
        # 
        self.looping = 0

            
    def registerMessages(self):        
        '''
        The purpose of this method is to declare the list of messages IDs for which we are interested to receive. 
        Here we are interested in a single message besides the standard list of message IDs returned by the
        base class.
        It is not necessary to include the list of messages from the base class but it contains some very useful
        message IDs like game_paused, game_resumed, etc., so most probably you will want to do this.
        '''
        return ['sound_finished'].extend(BaseNodeScript.registerMessages(self))
            
            
    def enter(self):
        '''
        Here we initialize some fields and flags and setup our UI which constists only of labels.
        '''
        
        # call the super class implementation first, this is optional
        BaseNodeScript.enter(self)
        
        self.sounds = self.game.getSoundsFx()
                
        # hold the camera fixed
        self.game.getView().getCameraController().disable()
        
        # display instructions
        self.instructions = OnscreenText(text = 'Press 1 for blah-blah, 2 for cling and 3 for zipper',
                                         pos = (base.a2dLeft + 0.1, 0.9),
                                         align = TextNode.ALeft,
                                         scale = 0.07,
                                         fg = (1.0, 1.0, 1.0, 1.0),
                                         shadow = (0.0, 0.0, 0.0, 0.7)
                                         )
        
        # gets the status of sounds
        self.lastStatus = self.sounds.isEnabled()
        
        self.soundsStatusText = OnscreenText(text = 'Sounds status: %s' % self.lastStatus,
                                             pos = (base.a2dLeft + 0.1, 0.8),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        
        self.volumeText = OnscreenText(text = 'Volume: %.1f' % self.sounds.getVolume(),
                                             pos = (base.a2dLeft + 0.1, 0.7),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        
        self.rateText = OnscreenText(text = 'Rate: %.1f' % self.sounds.getPlayRate(),
                                             pos = (base.a2dLeft + 0.1, 0.6),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        
        self.balanceText = OnscreenText(text = 'Balance: %.1f' % self.sounds.getBalance(),
                                             pos = (base.a2dLeft + 0.1, 0.5),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        
        self.loopText = OnscreenText(text = 'Looping: %d' % self.looping,
                                             pos = (base.a2dLeft + 0.1, 0.4),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        
        self.eventText = OnscreenText(text = 'Finished event received',
                                             pos = (base.a2dLeft + 0.1, 0.3),
                                             align = TextNode.ALeft,
                                             scale = 0.07,
                                             fg = (1.0, 0.0, 0.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        self.eventText.hide()
        
        OnscreenText(text = 'Press P, R to pause/resume playing sounds',
                                             pos = (base.a2dLeft + 0.1, 0.2),
                                             align = TextNode.ALeft,
                                             scale = 0.05,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        OnscreenText(text = 'Press L, Shift-L to increase/decrease the loop count',
                                             pos = (base.a2dLeft + 0.1, 0.1),
                                             align = TextNode.ALeft,
                                             scale = 0.05,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        OnscreenText(text = 'Press +, - to increase/decrease playing rate',
                                             pos = (base.a2dLeft + 0.1, 0.0),
                                             align = TextNode.ALeft,
                                             scale = 0.05,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        OnscreenText(text = 'Press [, ] to decrease/increase sound volume',
                                             pos = (base.a2dLeft + 0.1, -0.1),
                                             align = TextNode.ALeft,
                                             scale = 0.05,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        OnscreenText(text = 'Press D, E to disable/enable sounds',
                                             pos = (base.a2dLeft + 0.1, -0.2),
                                             align = TextNode.ALeft,
                                             scale = 0.05,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        OnscreenText(text = 'Press B, Shift-B to increase/decrease balance',
                                             pos = (base.a2dLeft + 0.1, -0.3),
                                             align = TextNode.ALeft,
                                             scale = 0.05,
                                             fg = (1.0, 1.0, 1.0, 1.0),
                                             shadow = (0.0, 0.0, 0.0, 0.7),
                                             mayChange = True
                                             )
        
        
        
        # add our input mappings to the active mappings, the existing mappings were not deleted
        # but they can be partially overridden by this.
        self.game.getInput().addMappings('sounds')
        
        
    def exit(self):
        '''
        Performs some cleanup.
        '''
        
        # call the super class implementation first, this is optional
        BaseNodeScript.exit(self)
        if self.instructions is not None:
            self.instructions.destroy()                
            
        # this will stop all active sounds
        if self.sounds is not None:
            self.sounds.stopAll()
            
            
    def update(self, millis):
        '''
        Gets called on every logic update and we use it to update the UI texts based on user input actions.
        The millis parameter is the milliseconds that elapsed since the last logic update.
        '''
        
        # call the super class implementation first, this is optional
        BaseNodeScript.update(self, millis)
        
        # detects if sounds status has been toggled in order to update the UI label
        if self.lastStatus != self.sounds.isEnabled():
            self.lastStatus = self.sounds.isEnabled()
            self.soundsStatusText.setText('Sounds status: %s' % self.lastStatus)
            
        # updates the volume label if needed
        if self.updateVolume:
            self.volumeText.setText('Volume: %.1f' % self.sounds.getVolume())
            self.updateVolume = False
        
        # updates the rate label if needed
        if self.updateRate:
            self.rateText.setText('Rate: %.1f' % self.sounds.getPlayRate())
            self.updateRate = False
            
        # updates the balance label if needed
        if self.updateBalance:
            self.balanceText.setText('Balance: %.1f' % self.sounds.getBalance())
            self.updateBalance = False
            
        # updates the looping label if needed
        if self.updateLooping:
            self.loopText.setText('Looping: %d' % self.looping)
            self.updateLooping = False
            
    
    def onInputAction(self, action):
        '''
        When an input action occurs the active nodescript will get notified through this method. 
        The given parameter is the name of the action that occured.
        Here we just branch based on the action name. You can see the defined actions of this example in data/example_sounds/sounds.mappings. 
        
        You return a True value to indicate that you handled the action and False to indicate that you ignored it.
        '''
        if action == "play_blah":
            '''
            We play the blah sound but keep a reference to it in order to have only one instance of this sound.
            The first time we call sounds.playSound to create the sound and get back a SoundPlaybackInterface 
            which we use for controlling playback. Notice that in the call to playSound we don't provide a filename.
            That's because the sound's properties, along with the filename, is defined in a .sound file name blah.sound.
            The file is located at data/example_sounds/blah.sound
            On subsequent invocations of this action we only call SoundPlaybackInterface.play() to get the sound
            playing.                        
            '''
            if self.blahSound is None:
                self.blahSound = self.sounds.playSound('blah', rate = self.sounds.getPlayRate(), loop = self.looping)
            else:
                self.blahSound.play()
                
        elif action == "play_cling":
            '''
            The sound is defined in data/example_sounds/cling.sound. We do not keep a reference to the playback interface
            here. Instead we create a new sound each time the action gets invoked.
            '''
            self.sounds.playSound('cling', rate = self.sounds.getPlayRate(), loop = self.looping)
            
        elif action == "play_zipper":
            '''
            For the zipper sound we instead provide a filename and use Sounds.playSoundFile for that purpose.
            We also don't keep a reference to the playback interface so a new sound is created each time.
            '''
            self.sounds.playSoundFile('zipper_bag_1.ogg', rate = self.sounds.getPlayRate(), loop = self.looping)
            
        elif action == "pause_sounds":            
            if self.blahSound is not None:
                self.blahSound.pause()
                
            # Sounds.pauseAll just pauses all currently playing sounds
            self.sounds.pauseAll()
            
        elif action == "resume_sounds":
            if self.blahSound is not None:
                self.blahSound.play()
                
            # Sounds.resumeAll just pauses all paused sounds
            self.sounds.resumeAll()    
            
        elif action == "enable_sounds":
            # Sounds.enableSounds enables global sound playback
            self.sounds.enableSounds()
            
        elif action == "disable_sounds":
            # Sounds.enableSounds disables global sound playback, a sound that was playing prior to this call will get stopped
            self.sounds.disableSounds()
            
        elif action == "increase_volume":
            # this demonstrates updating the properties of a single sound
            if self.blahSound is not None:
                self.blahSound.setVolume(self.sounds.getVolume() + 0.1)
                
            # while here we update the volume property affecting all sounds at the same time
            self.sounds.setVolume(self.sounds.getVolume() + 0.1)
            self.updateVolume = True
            
        elif action == "decrease_volume":
            # same here as we did with the increase_volume action
            if self.blahSound is not None:
                self.blahSound.setVolume(self.sounds.getVolume() - 0.1)
            self.sounds.setVolume(self.sounds.getVolume() - 0.1)
            self.updateVolume = True
            
        elif action == "increase_rate":
            # same here as we did with the increase_volume action
            if self.blahSound is not None:
                self.blahSound.setPlayRate(self.sounds.getPlayRate() + 0.1)
            self.sounds.setPlayRate(self.sounds.getPlayRate() + 0.1)
            self.updateRate = True
            
        elif action == "decrease_rate":
            # same here as we did with the increase_volume action
            if self.blahSound is not None:
                self.blahSound.setPlayRate(self.sounds.getPlayRate() - 0.1)
            self.sounds.setPlayRate(self.sounds.getPlayRate() - 0.1)
            self.updateRate = True
            
        elif action == "increase_balance":
            # same here as we did with the increase_volume action
            if self.blahSound is not None:
                self.blahSound.setBalance(self.sounds.getBalance() + 0.1)
            self.sounds.setBalance(self.sounds.getBalance() + 0.1)
            self.updateBalance = True
            
        elif action == "decrease_balance":
            # same here as we did with the increase_volume action
            if self.blahSound is not None:
                self.blahSound.setBalance(self.sounds.getBalance() - 0.1)
            self.sounds.setBalance(self.sounds.getBalance() - 0.1)
            self.updateBalance = True
            
        elif action == "increase_loop":
            # looping in this example only affects the blah sound
            self.looping += 1
            self.updateLooping = True
            if self.blahSound is not None:
                self.blahSound.setLoop(self.looping)
                
        elif action == "decrease_loop":
            self.updateLooping = True
            self.looping -= 1            
            if self.looping < 0:
                self.looping = 0            
            if self.blahSound is not None:
                self.blahSound.setLoop(self.looping)
                    
        else:
            # we didn't handle this, indicate it by returning False
            return False 
            
        # action was handled, return True
        return True    
    
    
    def onMessage(self, msg, *args):
        '''
        Using Messenger objects any game component can broadcast messages which will become available to the active
        nodescript through this method.
        The msg parameter is the name of the message, while *args is a list of arguments provided by the sender.
        
        Each nodescript must first declare the list of messages for which it is interested to receive. The list is declared
        in the NodeScript.registerMessages method.
        '''
        
        # When a sound has finished playing the sound_finished message is broadcasted. 
        # We handle it here to get notified when the blah sound has finished and update the UI accordingly.
        if msg == 'sound_finished':
            print 'FINISHED'
            self.eventText.setFg((1.0, 0.0, 0.0, 0.0))
            self.eventText.show()
            Sequence(
                     LerpColorScaleInterval(self.eventText, 0.5, (1,1,1,1), (1,1,1,0)),
                     LerpColorScaleInterval(self.eventText, 0.5, (1,1,1,0), (1,1,1,1))
                     ).start()
                
                        