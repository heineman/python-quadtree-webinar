"""
    Initial Quadtree implementation storing points using 
    integer-coordinate regions.
    
    Every Quad Node has four children, partitioning space accordingly based on 
    NE, NW, SW, SE quadrants. Each Node evenly divides quadrants. Each node 
    represents a square collection of points, evenly subdivided into four 
    children nodes, until leaf nodes representing an individual point. 
    
    The Quadtree implements set-semantics. This means there are no duplicate 
    (x, y) points in a quadtree.
"""

from adk.region import Region, X, Y
from quadtree.util import NW, NE, SW, SE

class QuadNode:
    
    def __init__(self, region, isFull = False):
        """Create empty QuadNode centered on origin of given region."""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, 
                       region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None] * 4
        self.full = isFull
    
    def isPoint(self):
        """
        Determine if associated region is a single point. Region is closed on min,
        open on max.
        """
        return self.region.x_min + 1 == self.region.x_max and self.region.y_min + 1 == self.region.y_max
    
    def add(self, pt):
        """Add pt to QuadNode."""
         
        # If full, nothing to add and return False
        # if an empty point, then make Full and return True
        if self.full:
            return False
        elif self.isPoint():
            self.full = True
            return True
        
        # Find quadrant into which point is to be inserted and create if empty
        quad = self.quadrant(pt)
        
        if self.children[quad] == None:
            self.children[quad] = QuadNode(self.subregion(quad))
            self.children[quad].add(pt)
        else:
            # Try to add point to child; if fail, then we fail too.
            if not self.children[quad].add(pt):
                return False  
     
        return True
    
    def subregion(self, quad):
        """Return region associated with given quadrant."""
        r = self.region
        if quad is NE:
            return Region(self.origin[X], self.origin[Y], r.x_max,        r.y_max)
        if quad is NW:
            return Region(r.x_min,        self.origin[Y], self.origin[X], r.y_max)
        if quad is SW:
            return Region(r.x_min,        r.y_min,        self.origin[X], self.origin[Y])
        if quad is SE:
            return Region(self.origin[X], r.y_min,        r.x_max,        self.origin[Y])
    
    def subdivide(self):
        """Add four children nodes to node, retaining full status of parent."""
        self.children[NE] = QuadNode(self.subregion(NE), self.full)
        self.children[NW] = QuadNode(self.subregion(NW), self.full)
        self.children[SW] = QuadNode(self.subregion(SW), self.full)
        self.children[SE] = QuadNode(self.subregion(SE), self.full)
    
    def quadrant(self, pt):
        """Determine quadrant in which point exists."""
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
        Create QuadTree defined over existing rectangular region. Assume that (0,0) is
        the lower left coordinate and the half-length side of any square in quadtree
        is power of 2. If incoming region is too small, this expands accordingly.    
        """
        self.root = None
        self.region = region
        
    def add(self, pt):
        """Add point to QuadTree. Return False if outside region or already exists."""
        if self.root is None:
            self.root = QuadNode(self.region)
            
        return self.root.add(pt)
    