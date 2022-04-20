#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 10:57:28 2021

@author: Julian Kaiser
"""
import cv2
import numpy as np
from threading import Thread
import time
import tkinter as tk

import matplotlib.pyplot as plt

from HintergrundAbziehen_GUI import removeBackgroundFit2, removeBackgroundFitIntegral, removeBackgroundFitPartial
import Basicfunctions_GUI as bsf


class AsyncBgRemove(Thread):
    def __init__(self, image, console, window_app):
        super().__init__()
        self.console = console
        self.image = image
        self.no_exception = True
        self.error = None
        self.mod = None
        self.y_fit = None
        self.r_squared = None
        self.window_app = window_app
        
        
    def run(self):
        try:
            print(self.window_app.settings_bgRemove_normal.get())
            if self.window_app.settings_bgRemove_normal.get() == 0: 
                self.image, self.mod, self.y_fit, self.r_squared = removeBackgroundFitPartial(self.image)
            else:
                self.image, self.mod, self.y_fit, self.r_squared = removeBackgroundFit2(self.image)
            self.no_exception = True
        except RuntimeError as err:
            self.no_exception = False
            self.error = err
        return
    
    def print_on_console_test(self, text=""):
        self.console.config(state=tk.NORMAL)
        self.console.insert('end', text + '\n')
        self.console.see(tk.END)        
        self.console.config(state=tk.DISABLED)
        
class AsyncBgRemoveForRaster(Thread):
    def __init__(self, filedirs, save_directory, filenames, window_app):
        super().__init__()
        self.filedirs = filedirs
        self.save_directory = save_directory
        self.filenames = filenames
        self.window_app = window_app
    
    def run(self):
        duration = (len(self.filedirs) - 1) * 9
        minutes = int((duration%3600)/60)
        sec = int((duration%60))
        self.window_app.print_on_console("Starting to remove the background from the selected raster. During this process the programm tend to be slower. The process takes approximately " + str(minutes) + "min and " + str(sec) + "s. Please don't close the application.")
        with_polyfit = self.window_app.settings_subtract_darkcurrent_with_poly.get()
        normal_bg_remove = self.window_app.settings_bgRemove_normal.get()
        
        for i in range(len(self.filedirs) - 1):
            try:
                file = cv2.imread(self.filedirs[i], -1)
                if normal_bg_remove == 0: 
                    return_image,_,_,_ = removeBackgroundFitPartial(file)
                else:
                    return_image,_,_,_ = removeBackgroundFit2(file)
                
                if with_polyfit:
                    print("im Polyfit")
                    diff_arr = np.copy(return_image)
                    delta = 40
                    mean = np.zeros((1286,))
                    for k in range(mean.shape[0]//2):
                        mean[k] = np.mean(return_image[k][delta:488-delta])
                        mean[643+k] = np.mean(return_image[k][488+delta:975-delta])
                    
                    bg_array = np.copy(return_image)
                    bg_array = bg_array.astype('float64')
                    bg_array[bg_array > ((np.max(mean)+40))] = np.nan     
                    bg_array = (bg_array).astype('uint16')
                    mblur = cv2.medianBlur(bg_array,3)
                    x = np.arange(0,975)
                    for j in range(mblur.shape[0]):
                        y_all = self.window_app.CalculateBgWithPoly(x, mblur[j][:], 10)
                        diff_arr[j][:] = diff_arr[j][:] - y_all
                    diff_arr[diff_arr < 0] = 0
                    cv2.imwrite(self.save_directory + self.filenames[i], diff_arr)
                else:
                    cv2.imwrite(self.save_directory + self.filenames[i], return_image)
            except:
                self.window_app.print_on_console("An Error occured while background remove from file" + str(self.filenames[i]) + ")! Please check the corresponding frame.")
        last = len(self.filedirs) - 1
        datei = open(self.filedirs[last],'r')
        text = datei.read()
        datei.close()
        with open(self.save_directory + self.filenames[last], 'w') as f:
            f.write(text)
        #cv2.imwrite(self.save_directory[last] + self.filenames[last], self.filedirs[last])
        self.window_app.print_on_console("Background remove from Raster done!")
        

class AsyncBgRemoveForSave(Thread):
    def __init__(self, image, path, comment, window_app, col, row, center_detect_queue=None, center_detect_save_dir=None, center_detect_bmp_save_dir=None):
        super().__init__()
        self.image = image
        self.path = path
        self.comment = comment
        self.window_app = window_app
        self.col = col
        self.row = row
        self.center_detect_queue = center_detect_queue
        self.center_detect_save_dir = center_detect_save_dir
        self.center_detect_bmp_save_dir = center_detect_bmp_save_dir
        
    def run(self):
        try:
            return_image,_,_,_ = removeBackgroundFit2(self.image)
            #TODO: schauen warum nur 255 bei continuous und nicht ganzes Intervall
            """
            print("vorher" + str(np.max(self.image)))
            print("nachher" + str(np.max(return_image)))
            print("vorher" + str(np.min(self.image)))
            print("nachher" + str(np.min(return_image)))
            """
            test = np.copy(return_image)
            cv2.imwrite(self.path + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + self.comment + "_removedBg_" + ".tif", test)
            if (self.center_detect_queue != None):
                min_value = int(np.min(return_image))
                max_value = int(np.max(return_image))
                
                for j in range(min_value+1, max_value+1):
                    image_cache = (255.0/(float(j) - float(min_value))) * np.subtract(return_image, min_value)
                    image_cache[image_cache < 0.0] = 0.0
                    image_cache[image_cache > 255.0] = 255.0
                    mean = np.mean(image_cache)
                    if np.abs(mean-70) < 0.5:
                        break
                
                filename = self.center_detect_bmp_save_dir + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + self.comment + "_optimized_contrast.bmp"
                cv2.imwrite(filename, image_cache)
                self.center_detect_queue.put((filename,self.center_detect_save_dir))
        except:
            self.window_app.print_on_console("An Error occured while background remove from frame (" + str(self.col) + "," + str(self.row) + ")! Please check the corresponding frame.")
        return 
    
    
class AsyncBgRemoveForNewEvaluation(Thread):
    def __init__(self, filelist, logfile, kontur, window_app, center_data=None):
        super().__init__()
        self.filelist = filelist
        self.logfile = logfile
        self.kontur = kontur
        self.window_app = window_app
        self.image = None
        self.center_data=center_data
        
    def run(self):
        settings_bgRemove_normal = self.window_app.settings_bgRemove_normal.get() 
        hits = np.zeros(self.kontur.shape)
        new_kontur = np.zeros(self.kontur.shape)
        delta = self.window_app.settings_polyfit_auto_delta_value
        increment = self.window_app.settings_polyfit_auto_increment_value
        #min_dots = 3
        duration = self.kontur.shape[0] * self.kontur.shape[1] * 7
        sec = int(duration % 60)
        minutes = int(duration // 60)
        self.window_app.print_on_console("The process takes about " + str(minutes) + "min and " + str(sec) + "s to finish. During this time, the program tends to be slower.")
        
        
        for i in range(len(self.filelist)-1):
            print("file " + str(i))
            position = (i//self.kontur.shape[1], i%self.kontur.shape[1])
            self.image = cv2.imread(self.filelist[i], -1)
            try:
                if settings_bgRemove_normal == 0: 
                    self.image, _, _, _ = removeBackgroundFitPartial(self.image)
                else:
                    self.image, _, _, _ = removeBackgroundFit2(self.image)                
                print("checkpoint 1")
                
                mean = np.zeros((1286,))
                for i in range(mean.shape[0]//2):
                    mean[i] = np.mean(self.image[i][delta:488-delta])
                    mean[643+i] = np.mean(self.image[i][488+delta:975-delta])
                
                self.image[self.image < int(np.max(mean)+increment)] = np.max(mean)+increment
                self.image = (self.image-np.min(self.image))*255.0/(np.max(self.image)-np.min(self.image))
                self.image = self.image.astype('uint8')
                
                print("checkpoint 2")
                
                mD, sD, current_image = bsf.maxFinder_large(self.image, None)
                plt.imshow(current_image)
                
                if len(mD) + len(sD) > 0:
                    hits[position] = len(mD) + len(sD)
                    new_kontur[position] = 2
                    
                print("checkpoint 3")
            except RuntimeError:
                self.window_app.print_on_console("An error occured at Frame " + str(position))
                
        
        average_dots = 0
        count = 0
        
        for j in range(new_kontur.shape[0]):
            for k in range(new_kontur.shape[1]):
                position = (j,k)
                if new_kontur[position] == 2:
                    average_dots = average_dots + hits[position]
                    count = count + 1
                    
        print("count " + str(count))
        print(hits)
        if count > 0:
            average_dots = int(average_dots / count)
            print("average dots " + str(average_dots))
            
            for l in range(new_kontur.shape[0]):
                for m in range(new_kontur.shape[1]):
                    position = (l,m)
                    print(hits[position])
                    print(hits[position] > average_dots)
                    if hits[position] > average_dots:
                            new_kontur[position] = 3
                            
        text = str(new_kontur)
        if self.center_data == None:
            with open(self.filelist[-1], 'w') as f:
                f.write(self.logfile + "#" + text)
        else:
            with open(self.filelist[-1], 'w') as f:
                f.write(self.logfile + "#" + text + "\n#" + self.center_data)
                    
            
class AsyncConvertionTifToBmp(Thread):
    def __init__(self, filedirs, save_directory, filenames, mean_to_scale, window_app):
        super().__init__()
        self.filedirs = filedirs
        self.save_directory = save_directory
        self.filenames = filenames
        self.mean_to_scale = mean_to_scale
        self.window_app = window_app
    
    def run(self):
        duration = (len(self.filedirs) - 1) * 2.17
        minutes = int((duration%3600)/60)
        sec = int((duration%60))
        self.window_app.print_on_console("Starting to optimize the contrast from the selected .tif-raster. During this process the programm tend to be slower. The process takes approximately " + str(minutes) + "min and " + str(sec) + "s. Please don't close the application.")
                
        for i in range(len(self.filedirs) - 1):
            try:
                image = cv2.imread(self.filedirs[i], -1)
                
                min_value = int(np.min(image))
                max_value = int(np.max(image))
                
                for j in range(min_value+1, max_value+1):
                    image_cache = (255.0/(float(j) - float(min_value))) * np.subtract(image, min_value)
                    image_cache[image_cache < 0.0] = 0.0
                    image_cache[image_cache > 255.0] = 255.0
                    mean = np.mean(image_cache)
                    if np.abs(mean-self.mean_to_scale) < 0.5:
                        break
                
                cv2.imwrite(self.save_directory + self.filenames[i][:-4] + ".bmp", image_cache)
            except:
                self.window_app.print_on_console("An Error occured while optimizing file" + str(self.filenames[i]) + ")! Please check the corresponding frame.")   

        
        last = len(self.filedirs) - 1
        datei = open(self.filedirs[last],'r')
        text = datei.read()
        datei.close()
        with open(self.save_directory + self.filenames[last], 'w') as f:
            f.write(text)
        self.window_app.print_on_console("Convertion from a .tif- to a .bmp-raster is done!")
            
                
            
            
            
            
            
            
            
            
            
            
            
            
            