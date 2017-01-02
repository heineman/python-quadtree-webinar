"""
    Initial Quadtree implementation storing points.
    
    Every QuadNode has four children, partitioning space accordingly based on NE, NW, SW, SE quadrants.
    Each QuadNode can store up to four points.
    
    Set-semantics where each point (x,y) is unique in a quadtree.
"""

from adk.region import Region, X, Y

# Each node can be subdivided into four quadrants.
NE = 0
NW = 1
SW = 2
SE = 3

class QuadNode:
    
    def __init__(self, region):
        """Create QuadNode centered on origin of given region."""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None]*4
        self.points = []
    
    def add (self, pt):
        """Add point to the QuadTree rooted at node."""
        node = self
        while node:
            if node.points is None: 
                # if interior node, find suitable child
                quad = node.quadrant (pt)
                node = node.children[quad]
            else:
                # Check if present in leaf node. Subdivide as necessary before adding
                if pt in node.points:
                    return False
                
                if len(node.points) == 4:
                    node.subdivide()
                    quad = node.quadrant (pt)
                    node = node.children[quad]
                else:
                    node.points.append(pt)
                    return True
    
    def subdivide(self):
        """Add four child nodes and reassign existing points."""
        region = self.region
        self.children[NE] = QuadNode(Region(self.origin[X], self.origin[Y], region.x_max,   region.y_max))
        self.children[NW] = QuadNode(Region(region.x_min,   self.origin[Y], self.origin[X], region.y_max))
        self.children[SW] = QuadNode(Region(region.x_min,   region.y_min,   self.origin[X], self.origin[Y]))
        self.children[SE] = QuadNode(Region(self.origin[X], region.y_min,   region.x_max,   self.origin[Y]))
        
        # go through our points and push to lowest children. 
        update = self.points
        self.points = []
        for pt in update:
            quad = self.quadrant(pt)
            self.children[quad].add(pt)
            
        # no longer capable of storing points, since interior node
        self.points = None
        
    def quadrant(self, pt):
        """Determine quadrant in which point exists. Closed intervals on quadrants I (NE) and III (SW)."""
        if pt[X] >= self.origin[X]:
            if pt[Y] >= self.origin[Y]:
                return NE
            else:
                return SE
        else:
            if pt[Y] >= self.origin[Y]:
                return NW
            else:
                return SW
   
class QuadTree:

    def __init__(self, region):
        """
        Create Quadtree defined over existing rectangular region. Assume that (0,0) is the center
        and half-length side of any square in quadtree is power of 2. If incoming region is too small, then
        this expands accordingly.    
        """
        self.root = None
        self.region = region
        
    def add(self, pt):
        """Add point to Quadtree."""
        if self.root is None:
            self.root = QuadNode(self.region)
            self.root.add(pt)
            return True
        
        return self.root.add (pt)
    