"""
     Visualize quadtree in separate window.
"""
from tkinter import Canvas, ALL, Toplevel
from tkinter.font import Font
from quadtree.draw_tree import DrawTree

class VisualizationWindow:
    def __init__(self, master, label=None):
        """label is function for DrawTree that takes node and returns int."""
        self.master = master
        self.frame = Toplevel(width=1024, height=512)
        self.canvas = Canvas(self.frame, width=1024, height=512)        

        # Initialize appropriate fonts to use
        DrawTree.smallFont = Font(family='Times', size='14')
        DrawTree.largeFont = Font(family='Times', size='24')
        
        self.frame.title("QuadTree Visualization")
        self.canvas.pack()
        self.label = label
        
        # React to window closure events
        self.frame.protocol("WM_DELETE_WINDOW", self.closed)
        self.done = False

    def clear(self):
        """Clear everything."""
        self.canvas.delete(ALL)

    def closed(self):
        """Once closed, stop all visualizations and destroy frame."""
        self.done = True
        self.frame.destroy()

    def plot(self, tree):
        """Given DrawTree information, plot the quadtree."""
        if self.done:
            return
        
        self.canvas.delete(ALL)
        if tree is None:
            return
        
        dt = DrawTree(tree, label=self.label)
        dt.layout()
        dt.format(self.canvas)
