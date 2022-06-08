# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 19:02:26 2022

@author: Julian
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageChops
import numpy as np
import cv2

from matplotlib import pyplot as plt

class OverlaySimulation():
    
    def __init__(self, window_app):
        self.window_app = window_app
        
        self.init_toplevel()
        
        self.init_canvas()
        
        #### Testing ###################################
        self.colors = ["red", "blue"]
        self.point_data = np.zeros((2,110,2))
        self.point_data[0,:,:] = np.array([np.tile(np.arange(100,201,10),10),np.repeat(np.arange(100,201,10),10)]).T
        self.point_data[1,:,:] = np.array([np.tile(np.arange(105,206,10),10),np.repeat(np.arange(100,206,10),10)]).T
        self.point_size = 3
        
        self.draw_points_on_canvas()
    
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
        
        self.var_array = np.copy(self.window_app.var_array)
        self.var_img = ImageTk.PhotoImage(image=Image.fromarray(self.window_app.var_array), master=self.canvas_frame)
        self.img_on_canvas = self.canvas.create_image((self.window_app.canvas_width / 2, self.window_app.canvas_height / 2), image=self.var_img)
        
    def draw_points_on_canvas(self):
        images = []
        for index,fill in enumerate(self.colors):
            fill = self.window_app.root.winfo_rgb(fill)
            image = Image.new('RGB', (self.window_app.canvas_width, self.window_app.canvas_height), color=0)
    
            for x,y in self.point_data[index,:,:]:
                ImageDraw.Draw(image).ellipse((x-self.point_size,y-self.point_size,x+self.point_size,y+self.point_size), fill=fill)
            
            images.append(image)
        
        out = images[0]
        for i in range(1,len(images)):
            out = ImageChops.add(out,images[i],0.5)
        
        grayscale_image = Image.fromarray(self.var_array)
        rgb_image = grayscale_image.convert('RGB')
        
        out_array = np.array(out)
        rgb_image_array = np.array(rgb_image)
        
        out_array[np.all(out_array == (0,0,0), axis=2),:] = rgb_image_array[np.all(out_array == (0,0,0), axis=2),:]
        
        self.var_img = ImageTk.PhotoImage(image=Image.fromarray(out_array), master=self.canvas_frame)
        self.canvas.itemconfig(self.img_on_canvas, image = self.var_img)
        
        return