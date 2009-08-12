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

import time
import math
import weakref

# This cache implementation is heavily based on the cache implementation found in PyQLogger's Cache.py module.
# For more info: http://pyqlogger.berlios.de/

class CacheItem(object):
    '''
    Represents a cached item. It is linked to the actual data through a weak reference.
    '''
    def __init__(self, name, data):
        '''
        @param name: The name of the item matches the respective key in the cache.
        @param data: The actual data.
        '''
        self.name = name
        self.setData(data)        
        self.accessTime = 0
        self.modTime = time.time()

    def getData(self):
        self.accessTime = time.time()
        return self.data() if type(self.data) == weakref else self.data

    def setData(self, data):
        self.modTime = time.time()
        try:
            # try to link through a weak reference, if it fails then link directly
            self.data = weakref.ref(data)
        except TypeError:
            self.data = data


class Cache(dict):
    '''
    Implements a cache that incorporates the LRU eviction strategy.

    Note: the data inserted in the cache are only weakly referenced therefore you must be prepared
    to deal with None return values.
    '''
    def __init__(self, name, size=128, maxAge = 60*60):
        '''
        @param name: A name that identifies this cache instance.
        @param size: Defines the size of the cache, i.e. the maximum count of items that it can contain.
        @param maxAge: Time in seconds before an item expires.
        '''
        self.items = {}
        self.size = size
        self.maxAge = maxAge

        self.insertions = 0
        self.requests = 0
        self.hits = 0
        self.purges = 0


    def getName(self):
        return self.name


    def setName(self, value):
        self.name = value


    def __setitem__(self, key, value):
        self.insertions += 1

        if (key not in self and self.size and len(self) >= self.size):
            self._evictLRU()

        dict.__setitem__(self, key, CacheItem(key, value))


    def __getitem__(self, key):
        self.requests += 1
        item = dict.__getitem__(self, key)
        if self._hasExpired(item):
            del self[key]
            return None
        else:
            self.hits = self.hits + 1
            return item.getData()


    def has_key(self, key):
        try:
            item = dict.__getitem__(self, key)
        except (KeyError):
            return False

        if self._hasExpired(item):
            return False
        else:
            return True


    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


    def values(self):
        '''
        @return: A list of all the data stored in the cache.
        '''
        return [dict.__getitem__(self, key).getData() for key in self]


    def items(self):
        '''
        @return: A list of tuples, where each tuple contains a key and its respective value in the cache.
        '''
        return map(None, self.keys(), self.values())

    def purge(self):
        '''
        Clears the cache.
        '''
        self.purges += 1
        dict.clear()

    def getStats(self):
        '''
        @return: A dictionary filled with statistics about the usage of this cache.
        '''
        return {
            'maxSize'    : self.size,
            'size'       : len(self),
            'insertions' : self.insertions,
            'requests'   : self.requests,
            'hits'       : self.hits,
            'misses'     : self.requests - self.hits,
            'purges'     : self.purges
        }

    def _hasExpired(self, item):
        return (time.time() - item.modTime) > self.maxAge


    def _getEvictSize(self):
        return math.floor(0.9*self.size)

    def _evictLRU(self):
        l = [(item.accessTime, item) for item in self.values()]
        l.sort()   # lru items appear first in the list
        for i in xrange(self._getEvictSize()):
            del self[ l[i][1].name ]


