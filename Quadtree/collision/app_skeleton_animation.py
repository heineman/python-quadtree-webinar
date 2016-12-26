"""
    Demonstration skeleton application for remaining apps.
    
    Left mouse click shows a fixed number of previous mouse clicks.
"""

from adk.region import X, Y
from tkinter import Tk, Canvas, ALL

numEvents = 10               # How many events to track
frameDelay = 25              # Ms between refresh events.

class SkeletonAnimationApp():
    def __init__(self, master):
        """Skeleton app to help understand more advanced ones."""
        
        master.title("Track mouse with up to " + str(numEvents) + " circles.") 
        self.master = master 
        
        # keep track of a fixed number of events
        self.events = []
        
        self.canvas = Canvas(master, width=512, height=512)        
        self.canvas.bind("<Motion>", self.track)
        self.canvas.pack()
        
        # Register handler which redraws everything at fixed interval
        self.master.after(frameDelay, self.drawEverything)
        
         
    def track(self, event):
        """Refresh event collection and redraw."""
        self.events.append((event.x, event.y))
        if len(self.events) > numEvents:
            del self.events[0]

    def drawEverything(self):
        """Draw at timed frequency."""
        self.master.after(frameDelay, self.drawEverything)
        self.visit()

    def visit (self):
        """ Visit structure and represent graphically."""
        self.canvas.delete(ALL)
        last = None
        for shape in self.events:
            self.canvas.create_oval(shape[X] - 4, shape[Y] - 4, 
                                 shape[X] + 4, shape[Y] + 4, fill='Black')
            if last:
                self.canvas.create_line(shape[X], shape[Y], last[X], last[Y])
            last = shape
            
if __name__ == "__main__":
    root = Tk()
    app = SkeletonAnimationApp(root)
    root.mainloop()