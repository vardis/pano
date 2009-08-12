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
import math, time, array, pickle
import json

from pandac.PandaModules import PNMImage, PNMPainter, PNMBrush, PNMImageHeader  
from pandac.PandaModules import Filename, VBase3, VBase4D

def clamp(x, low, high):
    if x < low:
        x = low
    elif x > high:
        x = high
    return x

class ImageMap(object):
    '''
    Maps image coordinates to hotspots' names. 
    It works by assigning an image that encodes the hotspots through color. A dictionary
    needs to also be specified in order to define the color encoding.
    For example, for the hotspot 'door' the encoding image might have blue over the 
    hotspot's region and the dictionary should have an entry such as: dict['door'] = (0, 0, 255)
    in order to map the name 'door' to the respective RGB color.    
    '''
    def __init__(self, name, imageFile = None, hotspots = None):
        '''
        @param name: A unique name for this resource.
        @param imageFile: The filename of the image that will provide the color encoding.
        @param hotspots: The dictionary that will map hotspots' names to RGB colors.
        '''
        self.name = name
        self.imageFile = imageFile
        
        # this will be initialized the associated ResourceLoader instance
        self.image = None        
        
        self.hotspots = {} if hotspots is None else hotspots        
            
        
    def getHotspot(self, x, y):
        '''
        Returns the hotspot at the x, y image coordinates.The image coordinates are assumed to start at the top
        left corner of the image and extend left-to-right and top-to-bottom.
        @param x: the relative x coordinate, lies in 0..1
        @param y: the relative y coordinate, lies in 0..1
        @return: the name of the found hotspot or None
        '''
        if self.image is not None:                        
            x = clamp(x*self.image.getXSize(), 0, self.image.getXSize())
            y = clamp(y*self.image.getYSize(), 0, self.image.getYSize())            
            col = self.image.getXel(x, y)
            col *= 255
                        
            for k, v in self.hotspots.items():
                if v[0] == col[0] and v[1] == col[1] and v[2] == col[2]:
                    return k
                

    def write(self, file):
        '''
        Serializes this instance to a file using JSON. 
        JSON was preferred in order to allow editing these files by hand.
        '''        
        file.write(json.dumps({'name' : self.name, 'imageFile' : self.imageFile, 'hotspots' : self.hotspots}, indent=4))
        
        
    def read(self, file):                
        '''
        Deserializes a instance marshalled using JSON.
        '''
        s = file.read()        
        d = json.loads(s)
        self.imageFile = d['imageFile']      
        self.name = d['name']
        self.hotspots = d['hotspots']
        
        print self.hotspots
        

class QuadTreeMap(object):
    '''
    Maps image coordinates to hotspots' names.
    It works in the same way as the ImageMap but uses a quadtree image representation for the encoding
    image. This can most of the time provide significant memory savings as this is a very compact representation.
    The higher the resolution of the encoding image, the higher will be the memory savings.
    '''
    def __init__(self, name, imageFile = None, metric = 2, maxDepth = 4):
        '''
        @param name: A unique name for this resource.
        @param imageFile: The filename of the image that will provide the color encoding.
        @param metric: The maximum color distance between the color assigned to a hotspot and the color of
        the point under consideration. If the color of the current point satisfies this metric, then the point
        is assumed to belong to the hotspot's area.  
        '''
        self.log = logging.getLogger('qmap')
        self.name = name
        self.quadTree = QuadTreeImage()
        self.hotspots = {}
        self.imageFile = imageFile
        self.metric = metric
        self.maxDepth = maxDepth
        self.bgCol = (255, 255, 255)        
            
    def setHotspots(self, hotspotsDict):
        self.hotspots = hotspotsDict
    
    def setBgColour(self, r, g, b):
        self.bgCol = (r, g, b)

    def getHotspot(self, x, y):
        '''
        Returns the hotspot at the x, y image coordinates. The image coordinates are assumed to start at the top
        left corner of the image and extend left-to-right and top-to-bottom.
        @param x: the relative x coordinate, lies in 0..1
        @param y: the relative y coordinate, lies in 0..1. 
        @return: the name of the found hotspot or None
        '''        
        if self.quadTree is not None:
            c = self.quadTree.getColourAt(x, y)
            if c is not None:
                return self._getClosestHotspot(c)
    
            
    def _getClosestHotspot(self, color):
        '''
        Calculates the color metric for all hotspots with the given color and returns the one with the lowest
        metric distance.
        '''
        min = 1000
        min_k = None
        for k, v in self.hotspots.items():
            ck = self.quadTree.colour_metric(v, color)
            if ck < min:
                min_k = k
                min = ck
                
        bgMetric = self.quadTree.colour_metric(self.bgCol, color) 
        if bgMetric < min:
            min_k = 'background'
            min = bgMetric
        return min_k
            
            
    def fromImage(self, img, metric = None, maxDepth = None, hotspots = None):
        '''
        Initializes an instance by providing a new color encoding image and optional criteria.
        @param imageFile: The filename of the image that will provide the color encoding.
        @param metric: The maximum color metric distance
        @param maxDepth: Specifies a maximum recursion depth for the tree's construction.
        @param hotspots: Updates the hotspots dictionary
        '''
        if metric is not None:
            self.metric = metric
            
        if maxDepth is not None: 
            self.maxDepth = maxDepth
            
        if hotspots is not None:
            self.hotspots = hotspots
            
        self.quadTree.fromImage(img, self.metric, self.maxDepth, True)

        nodeStack = [self.quadTree.root]
        numNodes = 1
        stripped = 1
        while not len(nodeStack) == 0:
            node = nodeStack.pop()
            children = []
            for i in (QuadTreeImage.NE, QuadTreeImage.NW, QuadTreeImage.SE, QuadTreeImage.SW):
                if node.subNodes[i]:
                    # no need to check for None because at this moment all nodes exist
                    n = node.subNodes[i]
                    if self._discardNode(n, node, self.metric):                    
                        stripped = stripped + 1                        
                        node.subNodes[i] = None
                    else:
                        numNodes = numNodes + 1
                        children.append(n)                    

            nodeStack.extend(children)
                    
        self.log.debug('stripped %i nodes\n' % stripped)
        self.log.debug('remained %i nodes\n' % numNodes)              
    
                
    def drawOnImage(self, img):
        '''
        Draws the quadtree on the given image.
        @param img: A PNMImage instance.
        '''
        painter = PNMPainter(img)
        painter.setFill(PNMBrush.makeTransparent())        
        self._drawImpl(painter, self.quadTree.root, 0, 0, 1)
        
        
    def _drawImpl(self, painter, node, x, y, level):
        dim = self.quadTree.w >> (level-1)        
        painter.drawRectangle(x, y, x + dim-1, y + dim-1)
        
        dim = self.quadTree.w >> level            
        if node.subNodes[QuadTreeImage.NE]:
            self._drawImpl(painter, node.subNodes[QuadTreeImage.NE], x + dim, y, level+1)
            
        if node.subNodes[QuadTreeImage.NW]:
            self._drawImpl(painter, node.subNodes[QuadTreeImage.NW], x, y, level+1)            
            
        if node.subNodes[QuadTreeImage.SE]:
            self._drawImpl(painter, node.subNodes[QuadTreeImage.SE], x + dim, y + dim, level+1)            
            
        if node.subNodes[QuadTreeImage.SW]:
            self._drawImpl(painter, node.subNodes[QuadTreeImage.SW], x, y+dim, level+1)            
                
                
    def _discardNode(self, n, parent, metricDistance):
        '''
        Decides if a node is not contributing any valuable information and can thus be discarded.
        @param n: The node under consideration
        @param parent: The node's parent, if any
        @param tolerance: The maximum color metric distance
        @return: True if the node can be discarded and False if otherwise.
        '''
        if parent.colour is not None and self.quadTree.colour_metric(n.colour, parent.colour) < 0.5:
            return True
        
        if n.colour[0] == self.bgCol[0] and n.colour[1] == self.bgCol[1] and n.colour[2] == self.bgCol[2]:
            return True
        
        if len([x for x in n.subNodes if x is not None]) == 0:
            for k, h in self.hotspots.items():                
                if self.quadTree.colour_metric(n.colour, h) <= metricDistance:
                    return False
                    
            return True
        
            
    def write(self, file):
        '''
        Serializes this instance to a file using Pickle.
        '''        
        pickle.dump(self, file, -pickle.HIGHEST_PROTOCOL)
        
        
    def read(self, file):                
        '''
        Deserializes a pickled instance.
        '''
        mask = pickle.load(file)
        self.quadTree = mask.quadTree
        self.hotspots = {}
        for k,v in mask.hotspots.items():
            self.hotspots[k] = v
        
        self.maxDepth = mask.maxDepth
        self.metric   = mask.metric                     
        

class QuadTreeImage(object):

    NE = 0
    NW = 1
    SE = 2
    SW = 3            
        
    def __init__(self, width = 1, height = 1, depth = 0):
        self._reset(width, height, depth)
        
        # the original width, height of the image
        self.ow = width
        self.oh = height
        
        self.log = logging.getLogger('quadTreeImage')        

    def _reset(self, w, h, d):                
        # the width and height which are a power of 2
        self.w, d1 = w,w
        self.h, d2 = h,h
        self.root = quadNode()
        self.depth = min((d, min((d1, d2))))

    
    def getColourAt(self, x, y):
        '''
        Returns the color of the image at the given point
        @param x: the relative x coordinate, lies in 0..1
        @param y: the relative y coordinate, lies in 0..1
        @return: a list containing the RGB components
        '''
        x = int(x*self.ow)
        y = int(y*self.oh)
        return self._getColourImpl(self.root, 0, 0, x, y, 0)
        
                    
    def _getColourImpl(self, node, nx, ny, x, y, level):        
        dim = self.w >> level        
        if nx <= x and ny <= y and (nx + dim) > x and (ny + dim) > y:
            if len([n for n in node.subNodes if n is not None]) == 0:                                        
                return node.colour
            else:                
                dim = dim >> 1
                c = None
                if node.subNodes[self.NE]:
                    c = self._getColourImpl(node.subNodes[self.NE], nx + dim, ny, x, y, level+1)
                    
                if c is None and node.subNodes[self.NW]:
                    c = self._getColourImpl(node.subNodes[self.NW], nx, ny, x, y, level+1)
                    
                if c is None and node.subNodes[self.SE]:
                    c = self._getColourImpl(node.subNodes[self.SE], nx + dim, ny + dim, x, y, level+1)
                    
                if c is None and node.subNodes[self.SW]:
                    c = self._getColourImpl(node.subNodes[self.SW], nx, ny + dim, x, y, level+1)
                
                return c                                   
                                      
                                                
    def next_pow_2(self, val):
        '''
        Returns the next power of 2 that is greater or equal than the given value.
        It also returns the exponent.
        '''
        base2 = 1
        for i in xrange(32):
            if val > base2:
                base2 *= 2
            else:
                return base2, i

    def colour_metric(self, c1, c2):
        '''
        Provides a metric for the difference between the given colours. 
        Each parameter should be an iterable of 3 values that represent an RGB triplet.
        '''
        # mean level of red
        r = ( c1[0] + c2[0] ) / 2.0
        
        dr = c1[0] - c2[0]
        dg = c1[1] - c2[1]
        db = c1[2] - c2[2]
        
        metric = math.sqrt( ((512.0 + r)/256.0)*dr*dr + 4.0*dg*dg + ((767 - r)/256.0)*db*db  )
        return metric


    def calculate_area_median_colour(self, buffer,  pitch, x, y, w, h):
        mr, mg, mb = 0.0, 0.0, 0.0
        offset = 3*x + y*pitch
        uniform = False
        r,g,b = buffer[offset], buffer[offset+1], buffer[offset+2]
        for col in xrange(w):
            idx1 = 3*col
            for row in xrange(h):
                idx = idx1 + pitch*row + offset
                r2, g2, b2 = buffer[idx], buffer[idx+1], buffer[idx+2]
                if r != r2 or g2 != g or b2 != b:
                    uniform = False
                mr += r2
                mg += g2
                mb += b2                
            
        inv_n = 1.0 / (w * h)
        return (mr * inv_n, mg * inv_n, mb * inv_n), uniform


    def subdv(self, node, buffer, pitch, tolerance, x, y, w, h, depth, dbgPainter):
        
        half_x = int(w / 2)
        half_y = int(h / 2)
        
        if depth == self.depth or half_x == 0 or half_y == 0:                                        
            # get unique colours
            cn = self._getUniqueColours(buffer, pitch, x, y, w, h)            
            if len(cn) == 2:
                # background and hotspot?
                total = w*h
                c1, c2 = cn[0], cn[1]                
                bg = None
                if c1[0] == 255 and c1[1] == 255 and c1[2] == 255:
                    bg = c1
                    other = c2
                elif c2[0] == 255 and c2[1] == 255 and c2[2] == 255:
                    bg = c2
                    other = c1
                
                if bg is not None:
                    bgCoverage = bg[3] / total
                    bias = 0.7
                    if bgCoverage < bias:                        
                        node.colour = other[:3]
                    else:
                        node.colour = bg[:3]
            return
                
        
        # calculate median colour of subregions         
        nw, u_nw = self.calculate_area_median_colour(buffer, pitch, x, y, half_x, half_y)
        ne, u_ne = self.calculate_area_median_colour(buffer, pitch, x+half_x, y, half_x, half_y)
        sw, u_sw = self.calculate_area_median_colour(buffer, pitch, x, y+half_y, half_x, half_y)
        se, u_se = self.calculate_area_median_colour(buffer, pitch, x+half_x, y+half_y, half_x, half_y)        
        
        # if the subregions exceed the metric's tolerance, the recursively subdivide
    #    if colour_metric(nw, ne) > tolerance or colour_metric(nw, sw) > tolerance or colour_metric(ne, se) > tolerance or colour_metric(sw, se) > tolerance or colour_metric(nw, se) > tolerance or colour_metric(sw, ne) > tolerance:
        do_sub = 0
        #print nw, ne, sw, se
            
        if self.colour_metric(nw, ne) > tolerance:            
            do_sub = 1
            
        elif self.colour_metric(nw, sw) > tolerance:            
            do_sub = 1
            
        elif self.colour_metric(ne, se) > tolerance:
            do_sub = 1
            
        elif self.colour_metric(sw, se) > tolerance:            
            do_sub = 1
            
        elif self.colour_metric(nw, se) > tolerance:            
            do_sub = 1
            
        elif self.colour_metric(sw, ne) > tolerance:            
            do_sub = 1
            
        if do_sub:        
            if not u_nw:
                n = quadNode(nw)                
                node.subNodes[self.NW] = n
                self.subdv(n, buffer,  pitch, tolerance, x, y, half_x, half_y, depth+1, dbgPainter)
                
            if not u_ne:
                n = quadNode(ne)                
                node.subNodes[self.NE] = n
                self.subdv(n, buffer,  pitch, tolerance, x+half_x, y, half_x, half_y, depth+1, dbgPainter)
                
            if not u_sw:
                n = quadNode(sw)                
                node.subNodes[self.SW] = n
                self.subdv(n, buffer,  pitch, tolerance, x, y+half_y, half_x, half_y, depth+1, dbgPainter)
                
            if not u_se:
                n = quadNode(se)                
                node.subNodes[self.SE] = n
                self.subdv(n, buffer,  pitch, tolerance, x+half_x, y+half_y, half_x, half_y, depth+1, dbgPainter)            
        else:            
            node.colour = nw    # whichever colour we pick is the same
        
    
    def fromImageFile(self, filename, tolerance = 2, max_depth = 5, debugOutput = False):
        # the source image
        img = PNMImage()

        if not img.read(Filename(filename)):
            self.log.error('Failed to read %s' % filename)
            return None 
        
        
    def fromImage(self, img, tolerance = 2, max_depth = 5, debugOutput = False):

        self.ow = img.getXSize()
        self.oh = img.getYSize()
        w, h = self.ow, self.oh
        
        expand = None
        if  (w & (w-1) != 0) or (h & (h-1) != 0):
            # resize to the next power of 2            
            w2 = self.next_pow_2(w)[0] if w & (w-1) != 0 else w
            h2 = self.next_pow_2(h)[0] if h & (h-1) != 0 else h
            self.log.debug('resizing to %i, %i' % (w2, h2))
            img.expandBorder(0, w2 - w, h2 - h, 0, VBase4D(0,0,0,0))
            expand = (w2-w, h2-h)
            w,h = w2,h2
            
        self._reset(w, h, max_depth)
        
        image_array = array.array('f')        
        for j in xrange(h):
            for i in xrange(w):
                el = img.getXel(i, j)
                image_array.append(255.0*el[0])
                image_array.append(255.0*el[1])
                image_array.append(255.0*el[2])                        

        self.log.debug('subdividing nodes...%s' % time.asctime())                    
        self.subdv(self.root, image_array, 3*w, tolerance, 0, 0, w, h, 0, None)        
        self.log.debug('done %s' % time.asctime())
        
        if expand is not None:
            img.expandBorder(0, -expand[0], -expand[1], 0, VBase4D(0,0,0,0)) 
                    
                    
    def _getUniqueColours(self, buffer, pitch, x, y, w, h):
        colours = []
        offset = 3*x + y*pitch
        for i in xrange(w):
            for j in xrange(h):
                idx = offset + 3*i + pitch*j
                r, g, b = buffer[idx], buffer[idx+1], buffer[idx+2]
                if len(colours) == 0:
                    colours.append([r, g, b, 1.0])
                else:
                    found = False
                    for c in colours:
                        if c[0] == r and c[1] == g and c[2] == b:
                            c[3] = c[3] + 1.0
                            found = True
                            break
                    if not found: 
                        colours.append([r, g, b, 1.0])
                        
        return colours
    
    
class quadNode(object):
    '''
    A node of a quadtree image for representing hotspots maps.
    '''
    def __init__(self, colour = None):                
        self.colour = colour
        self.subNodes = [None, None, None, None]
            

    