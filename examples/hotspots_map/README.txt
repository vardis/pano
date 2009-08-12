This example demonstrates the use of hotspot maps. Currently the only supported hotspot maps are images encoded 
as quadtree images which allow for a compact in-memory storage scheme. The higher is the resolution of the hotspots
image, the bigger the savings from the quadtree encoding.  The example demonstrates two different hotspot maps. 
No code is necessary for these examples but you will need to tweak the configuration in order to switch between
them.

The first, where the hotspot areas are distinct geometrical shapes with plenty of empty space between them is very 
simple and requires a very sparse quadtree for encoding. To run set initial_node = Shapes, width = 512 and height = 512.
The memory savings are:

size of hotspot image = (x * y) * bytesPerPixel = (800 * 600) * 3 = 786432 KB
size of quadtree encoded  image =  80 KB, depth: 7, metric: 2


In the second case the hotspot map is much more complex as the hotspots' areas must closely match the shape of the
continents in a world map. To run set initial_node = WorldMap, width = 500 and height = 320. 
The memory saving are:

size of hotspot image = (x * y) * bytesPerPixel = (500 * 320) * 3 = 480 KB
size of quadtree encoded  image =  385 KB, depth: 8, metric: 2
