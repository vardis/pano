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

class PandaUtil(object):
    '''
    Contains static utility methods for dealing with Panda3D related objects.
    '''

    def getFontPixelPerfectScale(font):
        '''
        Returns the font scale that will render this font with a one-to-one correspondence between texels
        and pixels.
        It assumes that the font will be parented to aspect2d and that the main window can be accessed by base.win . 
        '''
        winHeight = base.win.getYSize()
        ppu = font.getPixelsPerUnit()        
        return (2.0 * ppu) / winHeight
    
    def unitsToPixelsY(units, useAspect = True):    
        '''
        Translates the given world units to pixels along the vertical window dimension.
        If the parameter useAspect is True then the aspect ratio of the window will be considered.
        '''
        winHeight = float(base.win.getYSize())
        h = 2.0
        if useAspect:
            h = base.a2dTop - base.a2dBottom
        return winHeight * units / h
    
    def findSceneNode(nodeName, root = render):
        '''
        Searches for a scene node with the given name starting from the specified root node.
        @param nodeName: The name of the node to lookup.
        @param root: The node from which the search will initiate. It defaults to render.
        @return: A pandac.PandaModules.NodePath instance if the node was found or None.  
        '''
        np = root.find("**/" + nodeName)
        if np is None or np.isEmpty():
            return None
        else:
            return np
    
    getFontPixelPerfectScale = staticmethod(getFontPixelPerfectScale)
    unitsToPixelsY = staticmethod(unitsToPixelsY)
    findSceneNode = staticmethod(findSceneNode)
    

        