#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 10:40:52 2021

@author: Julian Kaiser
"""
import numpy as np
import Basicfunctions_GUI as bsf
from threading import Thread
import tkinter as tk
import os

class AsyncSnap(Thread):
    def __init__(self, exposure_time, window_app, stop_exposure_queue):
        super().__init__()
        self.exposure_time = exposure_time
        self.var_array = None
        self.window_app = window_app
        self.stop_exposure_queue = stop_exposure_queue
        
    def run(self):
        if self.window_app.has_moved and not(self.window_app.settings_12_bit_exposure.get()) and (self.exposure_time > 90):
            answer = tk.messagebox.askyesno("Sample has moved!", "You've moved the sample and exposure time is greater than 90s, so maybe the max. exposure time isn't correct any more. Do you want a new calculation for max. exposure?", icon=tk.messagebox.WARNING)
            #print(answer)
            if answer:
                self.window_app.snap_count(self.exposure_time, 30, True)
                return_image = bsf.longSecondExposure(30, self.stop_exposure_queue, 31, True)
                self.window_app.max_exposure = int(114000/(np.max(return_image) - 100))
                self.window_app.print_on_console("max. exposure: " + str(self.window_app.max_exposure) + "s")
        self.window_app.snap_count(self.exposure_time, self.exposure_time)
        if(not(self.window_app.settings_12_bit_exposure.get())):        
            self.var_array = bsf.longSecondExposure(self.exposure_time, self.stop_exposure_queue, self.window_app.max_exposure, True)
        else:
            self.var_array = bsf.longSecondExposure(self.exposure_time, self.stop_exposure_queue, self.window_app.max_exposure_PSL_Viewer, True)
        #print(np.max(self.var_array))
        if not(self.stop_exposure_queue.empty()):
            self.stop_exposure_queue.get()
            self.window_app.print_on_console("Stopping exposure ... done!")
        return
        #self.var_array,_,_ = bsf.laueClient("192.168.1.10",50000,"GetImage\n",True)
        
class AsyncSnapCalculateMaxExposure(Thread):
    def __init__(self, stop_exposure_queue):
        super().__init__()
        self.return_image = None
        self.stop_exposure_queue = stop_exposure_queue
        
    def run(self):
        self.return_image = bsf.longSecondExposure(30, self.stop_exposure_queue, 31, True)
        
class AsyncHelpGermanDisplay(Thread):
    def __init__(self):
        super().__init__()
        
    def run(self):
        cmd = 'evince ' + os.getcwd() + '/User_Guide_Laue_Camera_Application_Deutsch.pdf --page-index=1'
        os.system(cmd)
        
class AsyncHelpEnglishDisplay(Thread):
    def __init__(self):
        super().__init__()
        
    def run(self):
        cmd = 'evince ' + os.getcwd() + '/User_Guide_Laue_Camera_Application_English.pdf --page-index=1'
        os.system(cmd)
        
        