"""
    Quadtree implementation for storing points.
    
    Every Quad Node has up to four children, partitioning space accordingly based on 
    NE, NW, SW, SE quadrants. Each Node evenly divides quadrants. Each node can store
    4 points, after which it must be subdivided.
    
    A quadtree implements set-semantics. This means there are no duplicate (x, y)
    points in a quadtree.
    
    Actual point objects only exist within the leaf nodes.
    
    Note that this data structure is not suitable for collision detection of
    two-dimensional shapes, but is shown here as a starting data structure to 
    prepare for proper collision detection.
"""

from adk.region import X, Y, Region
from quadtree.util import smaller2k, larger2k, containsPoint, NE, NW, SW, SE

class QuadNode:
    
    def __init__(self, region, pt = None):
        """Create empty QuadNode centered on origin of given region."""
        self.region = region
        self.origin = (region.x_min + (region.x_max - region.x_min)//2, 
                       region.y_min + (region.y_max - region.y_min)//2) 
        self.children = [None] * 4
        
        if pt:
            self.points = [pt]
        else:
            self.points = []
    
    def countChildren(self):
        """Count number of actual children nodes."""
        if self.children is None:
            return 0
        
        count = 0
        for c in self.children:
            if c is not None:
                count += 1
                
        return count
    
    def add(self, pt):
        """Add pt to the QuadNode, if not already present."""
        # Doesn't fit in this node (sanity check: not truly needed since tree checks)
        if not containsPoint(self.region, pt):
            return False

        node = self
        while node:
            # if we have points, then we are leaf node. Check here
            if node.points != None:
                if pt in node.points:
                    return False

                # Add if room                
                if len(node.points) < 4:
                    node.points.append(pt)
                    return True
                else:
                    node.subdivide()
            
            # Find quadrant into which to add
            quad = node.quadrant(pt)
            if node.children[quad] is None:
                node.children[quad] = node.subquadrant(quad)
            node = node.children[quad]
            
        return False

    def remove(self, pt):
        """
        Remove pt from descendant of this tree, returning (newRoot,update), where
        update is True if the point was removed from tree rooted at self, and 
        newRoot is the new root for parent node to use.
        """
        if self.points is not None and pt in self.points:
            if len(self.points) == 1:
                return (None, True)
            else:
                idx = self.points.index(pt)
                del self.points[idx]
                return (self, True)
        
        quad = self.quadrant(pt)
        updated = False
        if self.children[quad]:
            self.children[quad],updated = self.children[quad].remove(pt)
            
        # if all children None, so are we, otherwise return self.
        if self.countChildren() == 0:
            return (None,updated)
    
        return (self, updated)

    def subquadrant(self, quad):
        """Create QuadNode associated with sub-quadrant for parent region."""
        r = self.region
        if quad == NE:
            return QuadNode(Region(self.origin[X], self.origin[Y], r.x_max,        r.y_max))
        elif quad == NW:
            return QuadNode(Region(r.x_min,        self.origin[Y], self.origin[X], r.y_max))
        elif quad == SW: 
            return QuadNode(Region(r.x_min,        r.y_min,        self.origin[X], self.origin[Y]))
        elif quad == SE:
            return QuadNode(Region(self.origin[X], r.y_min,        r.x_max,        self.origin[Y]))
        
    def subdivide(self):
        """Add up to four children nodes and reassign existing points."""
        self.children = [None] * 4
        
        for pt in self.points:
            quad = self.quadrant(pt)
            if self.children[quad] == None:
                self.children[quad] = self.subquadrant(quad)
            self.children[quad].add(pt)
            
        # no longer capable of storing points, since interior node
        self.points = None
    
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
     
    def preorder(self):
        """Pre-order traversal of tree rooted at given node."""
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
        Create QuadTree defined over existing rectangular region. Assume that (0,0) is
        the lower left coordinate and the half-length side of any square in quadtree
        is power of 2. If incoming region is too small, this expands accordingly.    
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
        """Add point to QuadTree."""
        # Not able to fit in this tree
        if not containsPoint(self.region, pt):
            return False

        if self.root is None:
            self.root = QuadNode(self.region, pt)
            return True
        
        return self.root.add(pt)
    
    def remove(self, pt):
        """Remove pt should it exist in tree."""
        if self.root is None:
            return False
        
        if not containsPoint(self.region, pt):
            return False
        
        self.root,updated = self.root.remove(pt)
        return updated
    
    def __contains__(self, pt):
        """Check whether exact point appears in QuadTree."""
        node = self.root
        while node:
            if node.points != None and pt in node.points:
                return True

            quad = node.quadrant(pt)
            node = node.children[quad]
    
        return False
    
    def __iter__(self):
        """Pre-order traversal of points in the tree."""
        if self.root:
            for node in self.root.preorder():
                if node.points:
                    for pt in node.points:
                        yield pt
        