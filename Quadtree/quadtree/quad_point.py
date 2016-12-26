"""
    Quadtree implementation for storing points.
    
    Every Quad Node has four children, partitioning space accordingly based on NE, NW, SW, SE quadrants.
    Each Node evenly divides quadrants. Each node can store 4 points, after which it must be subdivided
    to store additional points.
    
    The Quadtree implements set-semantics. This means there are no duplicate (x, y) points in a quadtree.
    
    Actual point objects only exist within the leaf nodes.
    
    Note that this data structure is not suitable for collision detection of
    two-dimensional shapes, but is shown here as a starting data structure to 
    prepare for the proper quadtree structure.
"""

import math
from adk.region import X, Y, Region

# each point (X,Y,RADIUS) represents a circle.
RADIUS=2

# Not needed, but included for descriptive coloring in GUI
MULTIPLE=4

NE = 0
NW = 1
SW = 2
SE = 3


def smaller2k(n):
    """
    Returns power of 2 which is smaller than n. Handles negative numbers.
    """
    if n == 0: return 0
    if n < 0:
        return -2**math.ceil(math.log2(-n))
    else:
        return 2**math.floor(math.log2(n))
    
def larger2k(n):
    """
    Returns power of 2 which is larger than n. Handles negative numbers.
    """
    if n == 0: return 0
    if n < 0:
        return -2**math.floor(math.log2(-n))
    else:
        return 2**math.ceil(math.log2(n))

def containsPoint(region, point):
    """Returns True if point contained in rectangle, closed on min and open on max."""
    if point[X] < region.x_min: return False
    if point[X] >= region.x_max: return False
    if point[Y] < region.y_min: return False
    if point[Y] >= region.y_max: return False
    
    return True

class QuadNode:
    
    def __init__(self, region, pt = None):
        """Create empty QuadNode centered on origin of given region."""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None] * 4
        
        if pt:
            self.points = [pt]
        else:
            self.points = []
    
    def add (self, pt):
        """Add (pt, data) to the QuadNode."""
        node = self
        while node:
            # Not able to fit in this region
            if not containsPoint (node.region, pt):
                return False
        
            # if we have points, then we are leaf node. Check here
            if node.points != None:
                if pt in node.points:
                    return False

                # Add if room                
                if len(node.points) < 4:
                    node.points.append (pt)
                    return True
            
            # Find quadrant into which to add
            q = node.quadrant (pt)
            if node.children[q] is None:
                # subdivide and reassign points to each quadrant. Then add point
                node.subdivide()
            node = node.children[q]
            
        return False

    def remove(self, pt):
        """Remove pt  from QuadNode. Does not adjust structure. Return True if updated information."""
        if self.points != None and pt in self.points:
            idx = self.points.index(pt)
            del self.points[idx]
            return True
            
        return False

    def subdivide(self):
        """Add four children nodes to node and reassign existing points."""
        region = self.region
        self.children[NE] = QuadNode(Region(self.origin[X], self.origin[Y], region.x_max,   region.y_max))
        self.children[NW] = QuadNode(Region(region.x_min,   self.origin[Y], self.origin[X], region.y_max))
        self.children[SW] = QuadNode(Region(region.x_min,   region.y_min,   self.origin[X], self.origin[Y]))
        self.children[SE] = QuadNode(Region(self.origin[X], region.y_min,   region.x_max,   self.origin[Y]))
        
        for pt in self.points:
            q = self.quadrant(pt)
            self.children[q].add(pt)
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
     
     
    def preorder(self):
        """Pre order traversal of tree rooted at given node."""
        yield self

        for node in self.children:
            if node:
                for n in node.preorder():
                    yield n

    def __str__(self):
        """toString representation."""
        return "[{} ({}): {},{},{},{}]".format(self.region, self.points, self.children[NE], self.children[NW], self.children[SW], self.children[SE])

class QuadTree:

    def __init__(self, region):
        """
        Create Quad Tree defined over existing rectangular region. Assume that (0,0) is the center
        and half-length side of any square in quadtree is power of 2. If incoming region is too small, then
        this expands accordingly.    
        """
        self.root = None
        self.region = region.copy()
        
        xmin2k = smaller2k(self.region.x_min)
        ymin2k = smaller2k(self.region.y_min)
        xmax2k = larger2k(self.region.x_max)
        ymax2k = larger2k(self.region.y_max)
        
        self.region.x_min = self.region.y_min = min(xmin2k, ymin2k)
        self.region.x_max = self.region.y_max = max(xmax2k, ymax2k)
        
    def add(self, pt):
        """Add point to Quad Tree."""
        if self.root is None:
            self.root = QuadNode(self.region, pt)
            return True
        
        return self.root.add (pt)
    
    def remove(self, pt):
        """Remove pt should it exist in tree."""
        n = self.root
        while n:
            if n.points:
                for i in range(len(n.points)):
                    if n.points[i] == pt:
                        del n.points[i]
                        return True

            q = n.quadrant(pt)
            if n.children[q] is None:
                return False
            else:
                n = n.children[q]
    
        return False
    
    def __contains__(self, pt):
        """Check whether exact point appears in Quadtree."""
        n = self.root
        while n:
            if n.points != None and pt in n.points:
                return True

            q = n.quadrant(pt)
            if n.children[q] is None:
                return False
            else:
                n = n.children[q]
    
        return False
    
    def __iter__(self):
        """In order traversal of elements in the tree."""
        if self.root:
            for e in self.root.preorder():
                yield e
        