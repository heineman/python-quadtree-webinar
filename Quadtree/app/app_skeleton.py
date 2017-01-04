"""
    Demonstration skeleton application for remaining apps.
    
    Left mouse click shows a fixed number of previous mouse clicks.
"""

from adk.region import X, Y
from tkinter import Tk, Canvas, ALL

# How many events to track
numEvents = 5               

class SkeletonApp():
    def __init__(self, master):
        """Skeleton app to help understand more advanced ones."""
        
        master.title("Click to add up to " + str(numEvents) + " circles.") 
        self.master = master 
        
        # keep track of a fixed number of clicked events
        self.clicked = []
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.pack()
         
    def click(self, event):
        """Refresh event collection and redraw."""
        self.clicked.append((event.x, event.y))
        if len(self.clicked) > numEvents:
            del self.clicked[0]
        self.visit()

    def visit (self):
        """Visit structure and represent graphically."""
        self.canvas.delete(ALL)
        for shape in self.clicked:
            self.canvas.create_oval(shape[X] - 4, shape[Y] - 4, 
                                    shape[X] + 4, shape[Y] + 4, fill='black')
            
if __name__ == '__main__':
    root = Tk()
    app = SkeletonApp(root)
    root.mainloop()
