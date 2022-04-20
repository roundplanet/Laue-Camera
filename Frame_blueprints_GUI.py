#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 11:07:23 2021

@author: Julian Kaiser
"""

import tkinter as tk
from tkinter import ttk


class FrameLabelEntry_pack():
    """
    FrameLabelEntry_pack(master, text_label="", entry_var=None, replace_komma=False)
    
    A class for a tkinter Frame filled with a ttk-label on the left and a tk-entry on the right side using the pack function.

    Attributes
    ----------
    master: tk-frame
        master of the generated frame 
    text_label: str
        text in the tk-label 
    entry_var: tk-variable
        tk-variable of the tk-entry 
    replace_komma: bool
        replaces each inserted komma in the entry by a dot if True 

    Methods
    -------
    change_komma_to_point_entry(event)
        replaces each inserted komma in the entry by a dot
    """
    
    def __init__(self, master, text_label="", entry_var=None, replace_komma=False):
        """
        Parameters
        ----------
        master: tk-frame
            master of the generated frame 
        text_label: str
            text in the tk-label
        entry_var: tk-variable
            tk-variable of the tk-entry
        replace_komma: bool
            replaces each inserted komma in the entry by a dot if True 
        """        
        
        self.frame = tk.Frame(master)
        
        self.label = ttk.Label(self.frame, text=text_label)
        self.label.pack(side = tk.LEFT)
        
        self.entry = tk.Entry(self.frame, bd=5, width=10, justify="right", textvariable=entry_var)
        self.entry.pack(side = tk.RIGHT)
        if replace_komma:
            self.entry.bind('<Key>', self.change_komma_to_point_entry)
        
        self.frame.pack(side=tk.TOP, fill='x')
        
    def change_komma_to_point_entry(self, event):
        """Replaces each inserted komma in the entry by a dot"""
        
        if int(event.keycode) in (91,59):
            self.entry.insert(tk.INSERT, '.')
            return 'break'
        
        
        
class LabelEntry_grid():
    """
    LabelEntry_grid(master, row_, column_,text_label="", entry_var=None, label_sticky='w', entry_sticky='e', replace_komma=False)
    
    A class for a ttk-label on the left and a tk-entry on the right side using the grid function inside the master frame in the corresponding row and column.

    Attributes
    ----------
    master: tk-frame
        master frame, in which the label and entry is packed
    row_: int
        specify the row inside the master frame
    column_: int
        specify the column inside the master frame
    text_label: str
        text in the tk-label 
    entry_var: tk-variable
        tk-variable of the tk-entry 
    label_sticky: str
        defines where the label is in its column ('w' for left, 'e' for right)
    entry_sticky: str
        defines where the entry is in its column ('w' for left, 'e' for right)
    replace_komma: bool
        replaces each inserted komma in the entry by a dot if True 

    Methods
    -------
    change_komma_to_point_entry(event)
        replaces each inserted komma in the entry by a dot
    """
    
    def __init__(self, master, row_, column_,text_label="", entry_var=None, label_sticky='w', entry_sticky='e', replace_komma=False):
        """
        Parameters
        ----
        master: tk-frame
            master frame, in which the label and entry is packed
        row_: int
            specify the row inside the master frame
        column_: int
            specify the column inside the master frame
        text_label: str
            text in the tk-label 
        entry_var: tk-variable
            tk-variable of the tk-entry
        label_sticky: str
            defines where the label is in its column ('w' for left, 'e' for right)
        entry_sticky: str
            defines where the entry is in its column ('w' for left, 'e' for right)
        replace_komma: bool
            replaces each inserted komma in the entry by a dot if True
        """
        
        self.label = ttk.Label(master, text=text_label)
        self.label.grid(row=row_, column=column_, sticky=label_sticky)
        
        self.entry = tk.Entry(master, bd=5, width=7, justify="right", textvariable=entry_var)
        self.entry.grid(row=row_, column=column_ + 1, sticky=entry_sticky)
        if replace_komma:
            self.entry.bind('<Key>', self.change_komma_to_point_entry)
        
    def change_komma_to_point_entry(self, event):
        """Replaces each inserted komma in the entry by a dot"""
        
        if int(event.keycode) in (91,59):
            self.entry.insert(tk.INSERT, '.')
            return 'break'
        
class FrameLabelCheckbutton_pack():
    """
    FrameLabelCheckbutton_pack(master, text_label="", checkbutton_var=None)
    
    A class for a tkinter Frame filled with a ttk-label on the left and a tk-checkbutton on the right side using the pack function.

    Attributes
    ----------
    master: tk-frame
        master of the generated frame 
    text_label: str
        text in the tk-label 
    checkbutton_var: tk-variable
        tk-variable of the tk-checkbutton 
    """
    
    def __init__(self, master, text_label="", checkbutton_var=None):
        """
        Parameters
        ----
        master: tk-frame
            master of the generated frame 
        text_label: str
            text in the tk-label 
        checkbutton_var: tk-variable
            tk-variable of the tk-checkbutton 
        """
        
        self.frame = tk.Frame(master)
        
        self.label = ttk.Label(self.frame, text=text_label)
        self.label.pack(side = tk.LEFT)
        
        self.checkbutton = tk.Checkbutton(self.frame, variable=checkbutton_var)
        self.checkbutton.pack(side = tk.RIGHT)
        
        self.frame.pack(side=tk.TOP, fill='x')
        
class LabelScaleEntry_grid():
    """
    LabelScaleEntry_grid(master, row_, text_label="", scale_from=0, scale_to=1, scale_command=None, scale_var=None, entry_var=None, replace_komma=False, entry_scale_scrollable=False)
    
    A class for a ttk-label on the left, a ttk-scale in the middle and a tk-entry on the right side using the grid function inside the master frame in the corresponding row.
    The entry shows the value of the scale-variable.

    Attributes
    ----------
    master: tk-frame
        master of the generated frame 
    row_: int
        specify the row inside the master frame
    text_label: str
        text in the tk-label 
    scale_from: int
        lower border of the scale 
    scale_to: int
        upper border of the scale 
    scale_command: function
        command which is executed if the scale is modified
    scale_var: tk-variable
        tk-variable of the scale
    entry_var: tk-variable
        tk-variable of the tk-entry
    replace_komma: bool
        replaces each inserted komma in the entry by a dot if True 
    entry_scale_scrollable: bool
        determine, if the value of the scale can be modified by scrolling while the mouse is over the entry or the scale
    
    Methods
    -------
    change_komma_to_point_entry(event)
        replaces each inserted komma in the entry by a dot
    change_by_mousewheel(event)
        changes the value of the scale after the event
    change_by_mousewheel_in(event)
        set the condition for changing to True
    change_by_mousewheel_out(event)
        set the condition for changing to False 
    """
    
    def __init__(self, master, row_, text_label="", scale_from=0, scale_to=1, scale_command=None, scale_var=None, entry_var=None, replace_komma=False, entry_scale_scrollable=False):
        """
        Parameters
        ----
        master: tk-frame
            master of the generated frame 
        row_: int
            specify the row inside the master frame
        text_label: str
            text in the tk-label 
        scale_from: int
            lower border of the scale 
        scale_to: int
            upper border of the scale 
        scale_command: function
            command which is executed if the scale is modified
        scale_var: tk-variable
            tk-variable of the scale
        entry_var: tk-variable
            tk-variable of the tk-entry
        replace_komma: bool
            replaces each inserted komma in the entry by a dot if True 
        entry_scale_scrollable: bool
            determine, if the value of the scale can be modified by scrolling while the mouse is over the entry or the scale. If true, the mousewheel and motion is binded to the entry.
        """
        
        self.label = ttk.Label(master, text=text_label)
        self.label.grid(row=row_, column=0, sticky = 'e')
        
        self.scale = ttk.Scale(master, from_=scale_from, to=scale_to, command=scale_command, variable=scale_var)
        self.scale.grid(row=row_, column=1)
        
        self.entry = tk.Entry(master, bd=5, width=10, justify="right", textvariable=entry_var)
        self.entry.grid(row=row_, column=2)
        if replace_komma:
            self.entry.bind('<Key>', self.change_komma_to_point_entry)
        
        self.scroll_faktor = 1
        self.scroll_diff = 1
        if entry_scale_scrollable:
            self.is_scrollable = False
            
            self.entry.bind('<MouseWheel>', self.change_by_mousewheel)
            self.entry.bind('<Button-4>', self.change_by_mousewheel)
            self.entry.bind('<Button-5>', self.change_by_mousewheel)
            self.entry.bind('<Enter>', self.change_by_mousewheel_in)
            self.entry.bind('<Leave>', self.change_by_mousewheel_out)
            
            self.scale.bind('<MouseWheel>', self.change_by_mousewheel)
            self.scale.bind('<Button-4>', self.change_by_mousewheel)
            self.scale.bind('<Button-5>', self.change_by_mousewheel)
            self.scale.bind('<Enter>', self.change_by_mousewheel_in)
            self.scale.bind('<Leave>', self.change_by_mousewheel_out)
            
    
    def change_komma_to_point_entry(self, event):
        """Replaces each inserted komma in the entry by a dot"""
        
        if int(event.keycode) in (91,59):
            self.entry.insert(tk.INSERT, '.')
            return 'break'
        
    def change_by_mousewheel(self, event):
        """Changes the value of the scale if the mousewheel is rotated"""
        
        if(self.is_scrollable):
            if event.delta > 0 or event.num == 4:
                self.scale.set(self.scale.get() + self.scroll_faktor * self.scroll_diff)
            if event.delta < 0  or event.num == 5:
                self.scale.set(self.scale.get() - self.scroll_faktor * self.scroll_diff)
                
    def change_by_mousewheel_in(self, event):
        """Mouse is on the scale or the entry, changing is allowed"""
        
        self.is_scrollable = True
        
    def change_by_mousewheel_out(self, event):
        """Mouse is not on the scale or the entry, changing is not allowed"""
        self.is_scrollable = False
        

class RasterFrame():
    """
    RasterFrame(master, number)
    
    A class for a labeld tkinter frame with all necessary entries and radiobuttons to set a raster. 

    Attributes
    ----------
    master: tk-frame
        master of the generated frame 
    number: int
        number of the frame
        
    Methods
    -------
    change_komma_to_point_entry(event)
        replaces each inserted komma in the entry by a dot
        
    Notes
    ----
    Structure is:
        - first row: two tk-radiobutton (continuous, additive)
        - second row: two LabelEntry ((height,width), scale)
        - third row: two LabelEntry (coord. (x0,y0), exp. time)
    LabelEntry for scale is provided with change_komma_to_point_entry.
    """
    
    def __init__(self, master, number):
        """
        Parameters
        ----------
        master: tk-frame
            master of the generated frame 
        number: int
            number of the frame
            
        Notes
        ----
        Structure is:
            - first row: two tk-radiobutton (continuous, additive)
            - second row: two LabelEntry ((height,width), scale)
            - third row: two LabelEntry (coord. (x0,y0), exp. time)
        LabelEntry for scale is provided with change_komma_to_point_entry.
        """
        self.LabelFrame = tk.LabelFrame(master, bd=2, text='raster ' + str(number) + ' settings', pady=5, width=370)
        
        self.radio_var = tk.IntVar(self.LabelFrame)
        self.radio_var.set(0)
        self.radio_0 = tk.Radiobutton(self.LabelFrame, text='continuous', variable=self.radio_var, value=1, pady=3)
        self.radio_1 = tk.Radiobutton(self.LabelFrame, text='additive', variable=self.radio_var, value=0, pady=3)
        self.radio_0.grid(row=0, column=2, columnspan=2, sticky='w')
        self.radio_1.grid(row=0, column=0, columnspan=2, sticky='w')
        
        self.h_w_var = tk.StringVar(self.LabelFrame)
        self.h_w_var.set("3,3")
        self.h_w_widgets = LabelEntry_grid(self.LabelFrame, 1,0, text_label='(height, width)', entry_var=self.h_w_var)
        self.h_w_widgets.entry.config(width=5)
        
        self.scale_var = tk.DoubleVar(self.LabelFrame)
        self.scale_var.set(0.5)
        self.scale_widgets = LabelEntry_grid(self.LabelFrame, 1,2, text_label=' scale', entry_var=self.scale_var)
        self.scale_widgets.entry.config(width=5)
        self.scale_widgets.entry.bind('<Key>', self.change_komma_to_point_scale_entry)
        
        self.coord_var = tk.StringVar(self.LabelFrame)
        self.coord_var.set("0,0")
        self.coord_widgets = LabelEntry_grid(self.LabelFrame, 2,0, text_label='coord. (x0,y0)', entry_var=self.coord_var)
        self.coord_widgets.entry.config(width=5)
        
        self.exposure_var = tk.IntVar(self.LabelFrame)
        self.exposure_var.set(14)
        self.exposure_widgets = LabelEntry_grid(self.LabelFrame, 2,2, text_label=' exp. time', entry_var=self.exposure_var)
        self.exposure_widgets.entry.config(width=5)
        
        self.LabelFrame.pack(pady=5)
        
    def change_komma_to_point_scale_entry(self, event):
        """Replaces each inserted komma in the entry by a dot"""
        if int(event.keycode) in (91,59):
            self.scale_widgets.entry.insert(tk.INSERT, '.')
            return 'break'
        
    
    