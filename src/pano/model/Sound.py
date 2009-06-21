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


class Sound:
    """
    Defines the properties of a game sound. Sound resources are defined in .snd files.
    """

    # Names of the various filters that can be applied to sounds.
    FT_Chorus = 1
    FT_Reverb = 2
    FT_PitchShift = 3
    FT_Flange = 4
    FT_Compress = 5
    FT_HighPass = 6
    FT_LowPass = 7
    FT_Distort = 8
    FT_Echo = 9
    FT_Normalize = 10
    FT_Parameq = 11

    # Types of positional sounds
    POS_None     = 0    # sound is not positional
    POS_Node     = 1    # sound is attached to a node
    POS_Hotspot  = 2    # sound is attached to a hotspot
    POS_Absolute = 3    # the configuration specifies the absolute coordinates of the sound


    def __init__(self, name, soundFile=None, volume=1.0, balance=0.0, node=None, cutOff=None, rate=1.0, subtitles=None):
        self.name = name            # the logical name of the sound
        self.soundFile = soundFile  # the filename of the actual sound data
        self.volume = volume        # the sound's volume
        self.balance = balance      # the sound's balance
        self.node = node            # the name of the node to attach this sound to        
        self.rate = rate            # the play rate
        self.loop = False           # True/False if the sound should loop, or an integer value specifying the loop count
        self.subtitles = subtitles  # the key of the message to display as subtitles to this sound
        self.positional = Sound.POS_None     # indicates if the sound is positional and the type of position

        # the following can be:
        # a) A tuple of three floats for absolute positioning
        # b) A string naming a scenegraph node or a hotspot
        self.pos = None
        self.filters = {}           # contains the active filters in the form {FT_Chorus : ChorusFilter(), ...}
    
    
    def setFilter(self, f):
        '''
        Activates the given sound filter.
        @param f: A filter properties instance that identifies the type of filter and configures
        the filter.
        '''
        self.filters[f.type] = f

    def getFilter(self, filterType):
        '''
        Returns the active filter of the specified type.
        @param filterType: A constant that specifies the type of filter.
        @return: The respective filter properties instance or None if no such filter type exists
        or there is no active filter of this type on this sound.
        '''
        return self.filters.get(filterType)

    def removeFilter(self, filterType):
        '''
        Removes a specific type of filter from this sound.
        @param filterType: The type of filter.
        '''
        if self.filter.has_key(filterType):
            del self.filters[filterType]

    def getActiveFilters(self):
        '''
        Gets the active filters for this sound.
        @return: A list of constants that identify each active filter.
        '''
        return self.filters.values()

    
class ChorusFilter(object):
    '''
    Placeholder for the properties of the chorus effect.
    It simulates several voices by playing up to 3 instances of the same sound along side with the original.
    The modulation and shifting of the copies are configured through the delay, rate, depth and feedpack parameters.
    '''
    
    def __init__(self, dryMix = 0.5, wet1 = 0.5, wet2 = 0.5, wet3 = 0.5, delay = 40, rate = 0.8, depth = 0.03, feedback = 0.0):
        '''
        @param dryMix:  Volume of original signal to pass to output.  0.0 to 1.0. Default = 0.5.
        @param wet1:  Volume of 1st chorus tap.  0.0 to 1.0.  Default = 0.5. 
        @param wet2:  Volume of 2nd chorus tap. This tap is 90 degrees out of phase of the first tap.  0.0 to 1.0.  Default = 0.5. 
        @param wet3 Volume of 3rd chorus tap. This tap is 90 degrees out of phase of the second tap.  0.0 to 1.0.  Default = 0.5. 
        @param delay:  Chorus delay in ms.  0.1 to 100.0.  Default = 40.0 ms. 
        @param rate:  Chorus modulation rate in hz.  0.0 to 20.0.  Default = 0.8 hz. 
        @param depth:  Chorus modulation depth.  0.0 to 1.0.  Default = 0.03. 
        @param feedback:  Chorus feedback.  Controls how much of the wet signal gets fed back into the chorus buffer.  0.0 to 1.0.  Default = 0.0. */
        '''
        self.type = Sound.FT_CHORUS
        self.dryMix = dryMix
        self.wet1 = wet1
        self.wet2 = wet2
        self.wet3 = wet3
        self.delay = delay
        self.rate = rate
        self.depth = depth
        self.feedback = feedback


class CompressFilter(object):
    '''
    Placeholder for the properties of the compress effect.
    Reduces the dynamic range of an audio signal hence amplifying the softer parts and reduce the loud sounds. 
    '''
    
    def __init__(self, threshold = 0, attack = 50, release = 50, gain = 0):
        '''
        @param threshold:  The level above which the signal is reduced (dB) in the range from -60 through 0. The default value is 0.  
        @param attack:  Gain reduction attack time (milliseconds), in the range from 10 through 200. The default value is 50. 
        @param release:  Gain reduction release time (milliseconds), in the range from 20 through 1000. The default value is 50. 
        @param gain:  Make-up gain (dB) applied after limiting, in the range from 0 through 30. The default value is 0. 

        '''
        self.type = Sound.FT_CHORUS
        self.threshold = threshold
        self.attack = attack
        self.release = release
        self.gain = gain


class DistortFilter(object):
    '''
    Placeholder for the properties of the distort effect.
    Distorts a sound analogous to the higher the value of the level parameter.
    '''
    
    def __init__(self, level = 0.5):
        '''
        @param level: Distortion value.  0.0 to 1.0.  Default = 0.5.
        '''
        self.type = Sound.FT_CHORUS
        self.level = level


class EchoFilter(object):
    '''
    Placeholder for the properties of the echo effect.
    Reverbs a sound by playing two copies of a sound whose delay is fixed over time.
    '''
    
    def __init__(self, drymix = 1.0, wetmix = 0.5, delay = 500, decay_ratio = 0.5):
        '''
        @param drymix: Volume of original signal to pass to output.  0.0 to 1.0. Default = 1.0. 
        @param wetmix:  Volume of echo signal to pass to output.  0.0 to 1.0. Default = 1.0. 
        @param delay:  Echo delay in ms.  10  to 5000.  Default = 500. 
        @param decay_ratio:  Echo decay per delay.  0 to 1.  1.0 = No decay, 0.0 = total decay (ie simple 1 line delay).  Default = 0.5. 
        '''
        self.type = Sound.FT_Chorus
        self.drymix = drymix
        self.wetmix = wetmix
        self.delay = delay
        self.decay_ratio = decay_ratio 


class FlangeFilter(object):
    '''
    Placeholder for the properties of the flange effect.
    Creates a "whoosing" sound by playing two copies of a sound whose delay is varied over time.
    '''
    
    def __init__(self, drymix = 0.45, wetmix = 0.55, depth = 1.0, rate = 0.1):
        '''
        @param drymix:  Volume of original signal to pass to output.  0.0 to 1.0. Default = 0.45. 
        @param wetmix:  Volume of flange signal to pass to output.  0.0 to 1.0. Default = 0.55. 
        @param depth:  Flange depth.  0.01 to 1.0.  Default = 1.0. 
        @param rate:  Flange speed in hz.  0.0 to 20.0.  Default = 0.1. 
        '''
        self.type = Sound.FT_Flange
        self.drymix = drymix
        self.wetmix = wetmix
        self.depth = depth
        self.rate = rate


class HighPassFilter(object):
    '''
    Placeholder for the properties of the high pass effect.
    Cuts off the low frequences of the audio signal.
    '''
    
    def __init__(self, cutoff_freq = 5000.0, reasonance_q = 1.0):
        '''
        @param cutoff_freq: Highpass cutoff frequency in hz.  10.0 to output 22000.0.  Default = 5000.0. 
        @param reasonance_q: Highpass resonance Q value.  1.0 to 10.0.  Default = 1.0. 
        '''
        self.type = Sound.FT_HighPass
        self.cutoff_freq = cutoff_freq
        self.reasonance_q = reasonance_q


class LowPassFilter(object):
    '''
    Placeholder for the properties of the low pass effect.
    Cuts off the high frequences of the audio signal.
    '''
        
    def __init__(self, cutoff_freq = 5000.0, reasonance_q = 1.0):
        '''
        @param cutoff_freq: Lowpass cutoff frequency in hz.  10.0 to output 22000.0.  Default = 5000.0. 
        @param reasonance_q: Lowpass resonance Q value.  1.0 to 10.0.  Default = 1.0. 
        '''        
        self.type = Sound.FT_LowPass
        self.cutoff_freq = cutoff_freq
        self.reasonance_q = reasonance_q


class NormalizeFilter(object):
    '''
    Placeholder for the properties of the normalize effect.
    Normalizes the amplitude of a sound based on the peaks within the signal.
    For example if the maximum peaks in the signal were 50% of the bandwidth, it would scale the whole sound by 2.
    '''
    
    def __init__(self, fadeTime = 5000.0, threshold = 0.1, maxAmp = 20):
        '''
        @param fadeTime: Time to ramp the silence to full in ms.  0.0 to 20000.0. Default = 5000.0. 
        @param threshold:  Lower volume range threshold to ignore.  0.0 to 1.0.  Default = 0.1.  Raise higher to stop amplification of very quiet signals. 
        @param maxAmp: Maximum amplification allowed.  1.0 to 100000.0.  Default = 20.0.  1.0 = no amplification, higher values allow more boost. 

        '''
        self.type = Sound.FT_Normalize
        self.fade_time = fadeTime
        self.threshold = threshold
        self.max_amp = maxAmp


class ParameqFilter(object):
    '''
    Placeholder for the properties of the parametric EQ effect.
    Controls the amplitude and bandwidth of a neighborhood of frequencies.
    '''
    
    def __init__(self, center_freq = 8000.0, bandwidth = 1.0, gain = 1.0):
        '''
        @param center_freq: Frequency center.  20.0 to 22000.0.  Default = 8000.0. 
        @param bandwidth:  Octave range around the center frequency to filter.  0.2 to 5.0.  Default = 1.0. 
        @param gain:  Frequency Gain.  0.05 to 3.0.  Default = 1.0.  
        '''
        self.type = Sound.FT_Parameq
        self.center_freq = center_freq
        self.bandwidth = bandwidth
        self.gain = gain


class PitchShiftFilter(object):
    '''
    Placeholder for the properties of the pitch shift effect.
    Alters the pitch of a sound.
    '''
    
    def __init__(self, pitch = 1.0, fft_size = 1024):
        '''
        @param pitch:  Pitch value.  0.5 to 2.0.  Default = 1.0. 0.5 = one octave down, 2.0 = one octave up.  
        1.0 does not change the pitch. 
        @param fft_size:  FFT window size.  256, 512, 1024, 2048, 4096.  Default = 1024.      
        '''
        self.type = Sound.FT_PitchShift
        self.pitch = pitch
        self.fft_size = fft_size
        self.overlap = 4


class ReverbFilter(object):
    '''
    Placeholder for the properties of the reverb effect.
    Simulates the effect of reverberation in an enclosed space.
    '''
    
    def __init__(self, drymix = 0.66, wetmix = 0.33, room_size = 0.5, damp = 0.5, width = 1.0):
        '''
        @param drymix:  Dry mix.  0.0 to 1.0.  Default = 0.66
        @param wetmix:  Wet mix.  0.0 to 1.0.  Default = 0.33
        @param room_size:  Roomsize. 0.0 to 1.0.  Default = 0.5 
        @param damp:  Damp.     0.0 to 1.0.  Default = 0.5                  
        @param width:  Stereo width. 0.0 to 1.0.  Default = 1.0 
        '''
        self.type = Sound.FT_Reverb
        self.drymix = drymix
        self.wetmix = wetmix
        self.room_size = room_size
        self.damp = damp
        self.width = width





