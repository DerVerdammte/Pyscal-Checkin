import tkinter as tk
from PIL import Image, ImageTk
import time
import os
#test

class Fullscreen():
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)  
        self.root.bind("<F11>",
                         lambda event: self.root.attributes("-fullscreen",
                                    not self.root.attributes("-fullscreen")))
        self.root.bind("<Escape>",
                         lambda event: self.root.attributes("-fullscreen",
                                    False))

def raise_frame(frame):
    frame.tkraise()

