import random

class Playlist:
    """
    Represents a list of music tracks which are to be played in a specific order.    
    """
    
    def __init__(self, name='', loop=False):
        self.__name = name
        self.tracks = []
        self.__loop = loop
        self.__volume = 1.0        
        
    def shuffle(self):
        """
        Shuffles the playlist.
        """
        if len(self.tracks) > 1:
            indices = range(1, len(self.tracks))
            random.shuffle(indices)
            
            newTracks = []
            for i in indices:
                newTracks.append(self.tracks[i])
            self.tracks = newTracks
    
    def getTrack(self, index):
        """
        Returns a tuple of the form (index, track_name, track_file) for the track at the
        specified position within the playlist.
        If index is out of bounds, None is returned.
        """
        if len(self.tracks) > index and index >= 0:
            t = self.tracks[index]
            return (index, t[0], t[1])
        else:
            return None
        
    
    def listTracks(self):
        """
        Returns a list of tuples of the form (index, track_name, track_file) for all available tracks.
        """
        tracks = []
        for i, t in enumerate(self.tracks):
            tracks.append((i, t[0], t[1]))
        return tracks
    
    def addTrack(self, name, file, pos = None):
        """
        Adds a new or existing track into the playlist at the specified position.
        If a position is not specified, the position will default to the end of the list.
        """
        # if the given pos is invalid, set it to the end of the list
        if pos is None:
            self.tracks.append((name, file))
        else:            
            self.tracks.insert(pos, (name, file))
            
    def nextIndex(self, i):
        """
        Returns the next available index for playing taking into account the looping option.
        """
        if i < 0:
            return 0
        
        if i == self.count() and not(self.loop):
            return i
        
        return (i + 1) % self.count()
    
    def previousIndex(self, i):
        """
        Returns the previous available index for playing taking into account the looping option.
        """
        if i == 0 and not(self.loop):
            return i
        
        return (i - 1) % self.count()
    
    def count(self):
        return len(self.tracks)

    def getName(self):
        return self.__name

    def getLoop(self):
        return self.__loop

    def setLoop(self, value):
        self.__loop = value

    def getVolume(self):
        return self.__volume


    def setVolume(self, value):
        self.__volume = value



    name = property(getName, None, None, "Name's Docstring")

    loop = property(getLoop, setLoop, None, "Loop's Docstring")

    volume = property(getVolume, setVolume, None, "Volume's Docstring")
    