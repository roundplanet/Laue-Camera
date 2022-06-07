# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 19:02:26 2022

@author: Julian
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class OverlaySimulation():
    
    def __init__(self, window_app):
        self.window_app = window_app
        
        self.init_toplevel()
        
        self.init_canvas()
    
    def init_toplevel(self):
        self.toplevel = tk.Toplevel(self.window_app.root)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel_cancel)
        self.toplevel.title("Overlay Simulation")
        
    def toplevel_cancel(self):
        self.toplevel.destroy()
        self.window_app.overlay_simulation_is_displayed = False
        
    def init_canvas(self):
        self.canvas_frame = tk.Frame(self.toplevel, width=self.window_app.canvas_width, height=self.window_app.canvas_height, bg="white")
        self.canvas_frame.grid(row=0, column=0)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=self.window_app.canvas_width, height=self.window_app.canvas_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.var_img = ImageTk.PhotoImage(image=Image.fromarray(self.window_app.var_array), master=self.canvas_frame)
        self.img_on_canvas = self.canvas.create_image((self.window_app.canvas_width / 2, self.window_app.canvas_height / 2), image=self.var_img)
        
    def update_canvas(self):
        return