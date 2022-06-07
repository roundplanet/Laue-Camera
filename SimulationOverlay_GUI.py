# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 19:02:26 2022

@author: Julian
"""

import tkinter as tk
from tkinter import ttk

class OverlaySimulation():
    
    def __init__(self, window_app):
        self.window_app = window_app
        
        self.toplevel = tk.Toplevel(self.window_app.root)
        self.init_toplevel()
        
        
    
    def init_toplevel(self):
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel_cancel)
        self.toplevel.title("Overlay Simulation")
        
    def toplevel_cancel(self):
        self.toplevel.destroy()
        self.window_app.overlay_simulation_is_displayed = False