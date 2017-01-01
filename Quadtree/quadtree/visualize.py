"""
     Visualize quadtree in separate window.
"""
from tkinter import Canvas, ALL, Toplevel
from tkinter.font import Font
from quadtree.draw_tree import DrawTree, layoutDrawTree

class VisualizationWindow:
    def __init__(self, master, label=None):
        """label is function for DrawTree that takes node and returns int."""
        self.master = master
        self.frame = Toplevel(width=1024, height=512)
        self.canvas = Canvas(self.frame, width=1024, height=512)        

        self.frame.title("QuadTree Visualization")
        self.canvas.pack()
        self.label = label
        print ("label is:" + str(self.label))

    def clear(self):
        """Clear everything."""
        self.canvas.delete(ALL)

    def plot(self, tree):
        """Given DrawTree information, plot the quadtree."""
        self.canvas.delete(ALL)
        if tree is None:
            return
        
        # Initialize fonts to use
        DrawTree.smallFont = Font(family='Times', size='14')
        DrawTree.largeFont = Font(family='Times', size='24')
        
        dt = DrawTree(tree, label=self.label)
        dt = layoutDrawTree(dt)
        dt.format(self.canvas, -1)
