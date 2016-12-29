"""
    Perform visual layout of quadtree in Tk canvas.

    Layout inspired by https://llimllib.github.io/pymag-trees/

"""

from quadtree.quad import QuadTree, RADIUS, MULTIPLE, NE, NW, SW, SE
from collections import defaultdict

def layoutDrawTree(tree):
    setupDrawTree(tree)
    addmodsDrawTree(tree)
    return tree

def setupDrawTree(tree, depth=0, nexts=None, offset=None):
    if nexts is None:  nexts  = defaultdict(lambda: 0)
    if offset is None: offset = defaultdict(lambda: 0)

    countChild = 0
    total = 0
    for quad in [NW, NE, SW, SE]:
        if tree.children[quad] is not None:
            countChild = countChild + 1
            setupDrawTree(tree.children[quad], depth+1, nexts, offset)
            total = total + tree.children[quad].x

    tree.y = depth
    
    if countChild == 0:
        place = nexts[depth]
        tree.x = place
    elif countChild == 1:
        place = tree.children[0].x - 1
    else:
        place = total / countChild

    offset[depth] = max(offset[depth], nexts[depth]-place)

    if len(tree.children):
        tree.x = place + offset[depth]

    nexts[depth] += 2
    tree.mod = offset[depth]

def addmodsDrawTree(tree, modsum=0):
    tree.x = tree.x + modsum
    modsum += tree.mod

    for quad in [NW, NE, SW, SE]:
        if tree.children[quad] is not None:
            addmodsDrawTree(tree.children[quad], modsum)            

class DrawTree(object):
    def __init__(self, qtnode, depth=0):
        self.x = -1
        self.magx = 30
        self.magy = 80
        self.width = 30
        self.height = 30
        self.y = depth
        self.node = qtnode
        self.children = [None] * 4
        for quad in [NW, NE, SW, SE]:
            if qtnode.children[quad] is not None:
                self.children[quad] = DrawTree(qtnode.children[quad], depth+1)
        self.mod = 0

    def middle(self):
        """middle point"""
        return (self.x*self.magx + self.width/2,
                self.y*self.magy + self.height/2)

    def format(self, canvas, font, orientation):
        """add to canvas."""
        for quad in [NW, NE, SW, SE]:
            if self.children[quad] is not None:
                mid = self.middle()
                child = self.children[quad].middle()
                canvas.create_line(mid[0], mid[1], child[0], child[1])
                self.children[quad].format(canvas, font, quad)

        colorToUse = 'white'
        if len(self.node.shapes) == 0:
            colorToUse = 'gray'
        canvas.create_rectangle(self.x*self.magx, self.y*self.magy,
                                self.x*self.magx+self.width, self.y*self.magy+self.height, fill=colorToUse);

        # draw corner in faint colors
        if orientation == NW:
            canvas.create_rectangle(self.x*self.magx,
                                    self.y*self.magy,
                                    self.x*self.magx+self.width/2, 
                                    self.y*self.magy+self.height/2,
                                    fill='#ffcccc')
        elif orientation == NE:
            canvas.create_rectangle(self.x*self.magx+self.width/2,
                                    self.y*self.magy,
                                    self.x*self.magx+self.width, 
                                    self.y*self.magy+self.height/2,
                                    fill='#ccffcc')
        elif orientation == SW:
            canvas.create_rectangle(self.x*self.magx,
                                    self.y*self.magy+self.height/2,
                                    self.x*self.magx+self.width/2, 
                                    self.y*self.magy+self.height,
                                    fill='#ccccff')
        elif orientation == SE:
            canvas.create_rectangle(self.x*self.magx+self.width/2,
                                    self.y*self.magy+self.height/2,
                                    self.x*self.magx+self.width, 
                                    self.y*self.magy+self.height,
                                    fill='#ccffff')

        canvas.create_text(self.x*self.magx+self.width/2, self.y*self.magy + self.height/2,
                           font=font,
                           width=self.width, text=str(len(self.node.shapes)))


    def prettyPrint(self):
        """pp out the tree"""
        print (str(self.x) + "," + str(self.y) + " " + str(self.node.region))
        for quad in [NW, NE, SW, SE]:
            if self.children[quad] is not None:
                self.children[quad].prettyPrint()
