"""
    Perform visual layout of quadtree in Tk canvas.

    Layout inspired by https://llimllib.github.io/pymag-trees/
    
    Accepts any structure that has 'children' list attribute with up to
    four child nodes.

    Note: Before use, must externally set the small/large fonts to use.
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

def layoutDrawTree(tree):
    """Compute the layout for a DrawTree."""
    setupDrawTree(tree)
    addmodsDrawTree(tree)
    return tree

def setupDrawTree(tree, depth=0, nexts=None):
    """Recursively assign (x,y) abstract values to each node in DrawTree."""
    if nexts is None:  nexts  = defaultdict(lambda: 0)

    x_min = 99999
    x_max = -99999
    
    # place self initially before children, and update next coordinate for node
    # on this same depth level (might not be a direct sibling)
    tree.x = nexts[depth]
    nexts[depth] += 2
    tree.y = depth
    
    # recursively process all descendant nodes, and determine min/max of direct children.
    for quad in range(len(tree.children)):
        if tree.children[quad] is not None:
            setupDrawTree(tree.children[quad], depth+1, nexts)
            x_min = min(x_min, tree.children[quad].x)
            x_max = max(x_max, tree.children[quad].x)

    # Move self to be middle of children. If no children, neutral. When 'mod' is 
    # set, all descendants of a node are shifted right (including that node). Otherwise
    # you only need to shift node to be in proper position. 
    child_mid = (x_min + x_max) / 2.0
    if child_mid < tree.x:
        tree.mod = tree.x - child_mid
    elif child_mid > tree.x:
        tree.x = child_mid
   

def addmodsDrawTree(tree, modsum=0):
    """Recursively offset nodes horizontally by computed 'mod' values."""
    tree.x += modsum
    modsum += tree.mod

    for quad in range(len(tree.children)):
        if tree.children[quad] is not None:
            addmodsDrawTree(tree.children[quad], modsum)            

class DrawTree(object):
    """
    Abstract representation of a quadtree, in preparation for visualization.
    Each DrawTree node is assigned an (x,y) integer pair where y reflects 
    the depth of the node (0=root) and x reflects the offset position within 
    that depth.

    Algorithm inspired by from https://llimllib.github.io/pymag-trees/
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

    def middle(self):
        """compute mid point for DrawTree node."""
        return (self.x*magx + node_w/2,
                self.y*magy + node_h/2)

    def format(self, canvas, orientation):
        """Crete visual representation of node on canvas."""
        for quad in range(len(self.children)):
            if self.children[quad] is not None:
                mid = self.middle()
                child = self.children[quad].middle()
                canvas.create_line(mid[0], mid[1], child[0], child[1])
                self.children[quad].format(canvas, quad)

        colorToUse = 'white'
        if self.label:
            ival = self.label(self.node)
            if ival == 0:
                colorToUse = 'gray'
        canvas.create_rectangle(self.x*magx, self.y*magy,
                                self.x*magx+node_w, self.y*magy+node_h, fill=colorToUse)

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

        # use small font for 10 and higher.
        font = DrawTree.largeFont
        text = ''
        if self.label:
            ival = self.label(self.node)
            text = str(ival)
            if ival > 9:
                font = DrawTree.smallFont
        
        canvas.create_text(self.x*magx+node_w/2,
                           self.y*magy + node_h/2,
                           font=font,
                           width=node_w, text=text)

    def prettyPrint(self):
        """pp out the tree for debugging."""
        print (str(self.x) + "," + str(self.y) + " " + str(self.node.region))
        for quad in range(len(self.children)):
            if self.children[quad] is not None:
                self.children[quad].prettyPrint()
