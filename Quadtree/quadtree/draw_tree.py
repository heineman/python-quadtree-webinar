"""
    Perform visual layout of quadtree in Tk canvas.

    Layout inspired by https://llimllib.github.io/pymag-trees/
    
    Accepts any structure that has 'children' list attribute with up to
    four child nodes. May still produce some layouts that have overlapping nodes
    but works for the most part.

    Note: Before use, must externally set the small/large fonts to use, otherwise
    the default one is likely too small to see.
    
    Multiple adjustNN code suggests different layout heuristics. One I would like
    to add is to ensure a node N's left-most child is to the right of the 
    right-most child of the left-sibling of N (read that twice and it makes sense).
    Possibly extend to descendant instead of just child.
"""

from quadtree.quad import NE, NW, SW, SE
from collections import defaultdict

# Width,height in pixels for the nodes.
node_w = 25
node_h = 25

# Magnification factor to convert abstract positioning from DrawTree into
# actual pixels. Note that width < magx and height < magy otherwise bad
# things happen.
magx = 30
magy = 80

class DrawTree(object):
    """
    Abstract representation of a quadtree, in preparation for visualization.
    Each DrawTree node is assigned an (x,y) integer pair where y reflects 
    the depth of the node (0=root) and x reflects the offset position within 
    that depth.

    Algorithm inspired by from https://llimllib.github.io/pymag-trees
    """
    
    # must be set externally after tk is initialized.
    smallFont = None
    largeFont = None
    
    def __init__(self, qtnode, depth=0, label=None):
        """Recursively construct DrawTree structure to parallel quadtree node."""
        self.label = label
        self.x = -1
        self.y = depth
        self.mod = 0
        self.node = qtnode
        self.children = [None] * 4

        for quad in range(len(qtnode.children)):
            if qtnode.children[quad] is not None:
                self.children[quad] = DrawTree(qtnode.children[quad], depth+1, label)

    def assign(self, depth, nexts):
        """
        Recursively assign (x,y) abstract values to each node in DrawTree.
        nexts is dictionary for next x-coordinate on given depth.
        """
        x_min = 99999
        x_max = -99999
        
        # place self initially before children, and update next coordinate for node
        # on this same depth level (might not be a direct sibling)
        self.x = nexts[depth]
        nexts[depth] += 2
        self.y = depth
        
        # recursively process descendant nodes, and determine min/max of children.
        for quad in range(len(self.children)):
            if self.children[quad] is not None:
                self.children[quad].assign(depth+1, nexts)
                x_min = min(x_min, self.children[quad].x)
                x_max = max(x_max, self.children[quad].x)
    
        # Move self to be middle of children. If no children, do nothing. When 'mod'
        # is set, all descendants of a node are shifted right during adjust().
        # Otherwise you only need to shift self node to be in proper position 
        # relative to its children.
        if x_min != 99999:
            child_mid = (x_min + x_max) / 2.0
            if child_mid < self.x:
                self.mod = self.x - child_mid
                nexts[depth+1] += self.mod       # Affects next children placement
            elif child_mid > self.x:
                self.x = child_mid
                nexts[depth] = max(nexts[depth] + 2, self.x + 2)

    def adjust(self, modsum=0):
        """Adjust descendants based on computed 'mod' shift in recursion."""
        self.x += modsum
        modsum += self.mod

        for quad in range(len(self.children)):
            if self.children[quad] is not None:
                self.children[quad].adjust(modsum)       

    def middle(self):
        """Compute mid point for DrawTree node."""
        return (self.x*magx + node_w/2,
                self.y*magy + node_h/2)

    def layout(self):
        """
        Compute the layout for a DrawTree. In first recursive traversal, assign
        abstract coordinates for each node. In second traversal, shift nodes, as 
        needed, based on orientation with regards to their children.
        """
        # use defaultdict (with default of 0) for each level to start at left.
        self.assign(0, defaultdict(int))
        self.adjust(0)

    def format(self, canvas, orientation=-1):
        """
        Create visual representation of node on canvas.
        
        Represent children node with inner colored rectangle as visual cue.
        """
        for quad in range(len(self.children)):
            if self.children[quad] is not None:
                mid = self.middle()
                child = self.children[quad].middle()
                canvas.create_line(mid[0], mid[1], child[0], child[1])
                self.children[quad].format(canvas, quad)

        color = 'white'
        if self.label:
            ival = self.label(self.node)
            if ival == 0:
                color = 'gray'
        canvas.create_rectangle(self.x*magx, self.y*magy,
                                self.x*magx+node_w, self.y*magy+node_h, fill=color)

        # draw corner in faint colors
        if orientation == NW:
            canvas.create_rectangle(self.x*magx,
                                    self.y*magy,
                                    self.x*magx+node_w/2, 
                                    self.y*magy+node_h/2,
                                    fill='#ffcccc')
        elif orientation == NE:
            canvas.create_rectangle(self.x*magx+node_w/2,
                                    self.y*magy,
                                    self.x*magx+node_w, 
                                    self.y*magy+node_h/2,
                                    fill='#ccffcc')
        elif orientation == SW:
            canvas.create_rectangle(self.x*magx,
                                    self.y*magy+node_h/2,
                                    self.x*magx+node_w/2, 
                                    self.y*magy+node_h,
                                    fill='#ccccff')
        elif orientation == SE:
            canvas.create_rectangle(self.x*magx+node_w/2,
                                    self.y*magy+node_h/2,
                                    self.x*magx+node_w, 
                                    self.y*magy+node_h,
                                    fill='#ccffff')

        # use small font for values 10 and higher.
        font = DrawTree.largeFont
        text = ''
        if self.label:
            ival = self.label(self.node)
            text = str(ival)
            if ival > 9:
                font = DrawTree.smallFont
        
        canvas.create_text(self.x*magx + node_w/2,
                           self.y*magy + node_h/2,
                           font=font,
                           width=node_w, text=text)

    def prettyPrint(self, indent=''):
        """Print out the tree for debugging."""
        print (indent + str(self.x) + "," + str(self.y) + " " + str(self.node.region))
        for quad in range(len(self.children)):
            if self.children[quad] is not None:
                self.children[quad].prettyPrint(indent + '  ')
