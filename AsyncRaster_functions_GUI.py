#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 10:46:13 2021

@author: Julian Kaiser & Marvin Klinger
"""
import cv2
import numpy as np
from threading import Thread
import os
import datetime as dt
import time

import Basicfunctions_GUI as bsf
import AsyncBackgroundRemove_functions_GUI as abf


"""
Test
"""

class AsyncRaster(Thread):
    def __init__(self, hight, width, scale, exposure_time,y0,x0, window_app, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, center_detection_queue, is_continuous = False):
        super().__init__()
        self.hight = hight
        self.width = width
        self.scale = scale
        self.exposure_time = exposure_time * 1000
        self.coordinates = (y0,x0)
        self.window_app = window_app
        self.filelist = []
        self.is_continuous = is_continuous
        self.save_directory = window_app.save_directory
        self.stop_exposure_queue = stop_exposure_queue
        self.request_kontur_queue = request_kontur_queue
        self.request_cur_det_max_queue = request_cur_det_max_queue
        self.center_detection_queue = center_detection_queue
        

    def run(self):

        #initial constants
        minimum_time_for_dotsearch = 4999  #in ms of exposure
        aperture_value = 2  #number written onto the X-Ray aperture
        #exposure_time = 5000
        
        #calibration array [stage][aperture_value] = data
        stddev_comparison_array = np.array([[175, 145, 105, 0],
                                            [170, 130, 110, 0],
                                            [162, 120, 90, 0],
                                            [0, 0, 0, 0]])
        
        #similar to stddev_comparison_array but for long exposures
        sddev_longexposure_value = np.array([190,185,190,100])
        
        print(stddev_comparison_array[2][aperture_value - 1])
        offset = (self.coordinates[1], -self.coordinates[0])
        
        #initialie the containers
        result = np.zeros((self.hight, self.width))
        stddev = np.zeros(result.shape)
        avg = np.zeros(result.shape)
        treffer = np.ones(result.shape, np.uint8)
        
        #timing calculations
        #TODO: noch anpassen generell aber vor allem auf max_exposure Bestimmung
        if self.exposure_time <= 16000:
            bsf.setExposure(self.exposure_time)
        
        duration = 0.0
        if self.is_continuous:
            if(self.exposure_time/1000 < 90):
                duration = result.shape[0] * result.shape[1] * (self.exposure_time + 2000)
            elif self.window_app.settings_calculate_max_exposure_during_raster.get() and (self.exposure_time/1000 > 90):
                duration = result.shape[0] * result.shape[1] * (self.exposure_time + 6000 + 30000)
            else:
                duration = result.shape[0] * result.shape[1] * (((self.window_app.max_exposure + 2000)*self.exposure_time//self.window_app.max_exposure) + self.exposure_time%self.window_app.max_exposure + 2000)
        else:
            duration = result.shape[0] * result.shape[1] * (18000*(self.exposure_time//16000) + (self.exposure_time%16000 + 2000))
        seconds = duration/1000
        days = int(seconds/86400)
        hours = int((seconds%86400)/3600)
        minutes = int((seconds%3600)/60)
        sec = int((seconds%60))
        
        print("Approximate duration: " + str(days) + "days, " + str(hours) + "h, " + str(minutes) + "min, " + str(sec) + "sec")
        self.window_app.print_on_console("Approximate raster duration: " + str(days) + "days, " + str(hours) + "h, " + str(minutes) + "min, " + str(sec) + "sec")
        
        now = dt.datetime.now()
        time_necessary = dt.timedelta(days = days, hours = hours, minutes = minutes, seconds = sec )
        finish = now + time_necessary
        string = "%02d-%02d %02d:%02d" % (finish.day, finish.month, finish.hour, finish.minute)
        self.window_app.print_on_console("Approximate finish: " + string)
        
        #create save directory
        
        ordner_name = self.window_app.settings_file_prefix + "_RASTER_" + str(int(self.exposure_time/1000)) + "s_" + str(self.width) + "x" + str(self.hight) + "_" + str(self.scale) + "mm"
        
        self.save_directory = self.save_directory + "/" + ordner_name
        
        if(self.is_continuous):
            self.save_directory = self.save_directory + "_continuous"
        else:
            self.save_directory = self.save_directory + "_additive"
        
        self.check_save_directory()
        saveDirectory =  self.save_directory + "/"
        saveDirectoryOrginal = self.save_directory + "/Original_Pictures"
        os.makedirs(saveDirectoryOrginal)
        isAllowedToSubtractBg = False
        isAllowedToCaluclateMaxExposure = self.window_app.settings_calculate_max_exposure_during_raster.get()
        only12BitImage = self.window_app.settings_12_bit_exposure.get()
        if (self.window_app.settings_bgRemove_during_raster.get() and ((self.exposure_time/1000) > 59.9)):
            saveDirectoryOrginalBgRemoved = self.save_directory + "/Original_Pictures_Bg_Removed"
            os.makedirs(saveDirectoryOrginalBgRemoved)
            isAllowedToSubtractBg = True
            
        isAllowedToDetectCenter = False
        if (self.window_app.settings_center_detection_during_raster.get() and ((self.exposure_time/1000) > 89.9)):
            isAllowedToDetectCenter = True
            saveDirectoryCenterDetection = self.save_directory + "/Center_Detection_Results/"
            os.makedirs(saveDirectoryCenterDetection)
            saveDirectoryCenterDetectionWholeResults = self.save_directory + "/Center_Detection_Results/whole_results/"
            os.makedirs(saveDirectoryCenterDetectionWholeResults)
            if isAllowedToSubtractBg:
                saveDirectoryCenterDetectionOptimizedContrastBmp = self.save_directory + "/Center_Detection_Results/bmp_optimized_contrast/"
                os.makedirs(saveDirectoryCenterDetectionOptimizedContrastBmp)
            if (self.window_app.settings_center_detection_save_info_images_raster.get()):
                saveDirectoryCenterDetectionInfoImages = self.save_directory + "/Center_Detection_Results/info_images/"
                os.makedirs(saveDirectoryCenterDetectionInfoImages)
        
        for col in range(result.shape[0]):
            
            #Move in x-axis
            #print(str((col - (result.shape[0]-1)/2.0)*scale) + str(offset[0]) + " = " + str((col - (result.shape[0]-1)/2.0)*scale + offset[0]))
            print("move x:")
            xpos = (col - (result.shape[0]-1)/2.0)*self.scale + offset[0]
            bsf.motorClient('M', 'X', xpos)
            
            for row in range(result.shape[1]):
                                
                #Move in y-axis
                print("move y:")
                ypos = ((result.shape[1]-1)/2.0 - row)*self.scale + offset[1]
                bsf.motorClient('M', 'Y', ypos)
                
                #Take the picture
                if self.is_continuous:
                    if not(only12BitImage):
                        if(self.exposure_time/1000 < 90):
                            image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, int(self.exposure_time/1000), True)
                        elif isAllowedToCaluclateMaxExposure and (self.exposure_time/1000 > 90):
                            return_image = bsf.longSecondExposure(30, self.stop_exposure_queue, 31, True)
                            self.window_app.max_exposure = int(114000/(np.max(return_image) - 100))
                            image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, self.window_app.max_exposure, True)
                        else:
                            image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, self.window_app.max_exposure, True)
                    else:
                        image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, self.window_app.max_exposure_PSL_Viewer)
                    scaleMean, scaleStddev = cv2.meanStdDev(image)
                
                else:
                    if self.exposure_time > 16000:
                        image = bsf.longExposure(self.exposure_time/1000, self.stop_exposure_queue)
                        scaleMean, scaleStddev = cv2.meanStdDev(image)
                        
                    else:
                        bsf.tC("192.168.1.10", 50000, "Snap\n")
                        for i in range(int(self.exposure_time/1000) + 1):
                            if not(self.stop_exposure_queue.empty()):
                                bsf.tC("192.168.1.10", 50000, "Stop\n")
                                return_array = (127 * np.ones((643,975)))
                                return_array[0][0] = 0
                                return_array[1][0] = 255
                                image = return_array
                            time.sleep(1) 
                        image, rawMean, rawStddev, scaleMean, scaleStddev = bsf.laueClient("192.168.1.10",50000,"GetImage\n")
                        #print("RawMean, RawStddev, sMean, sStddev: " + str(rawMean) + " " + str(rawStddev) + " " + str(scaleMean) + " " + str(scaleStddev) + " ")
                
                if not(self.stop_exposure_queue.empty()):
                    self.stop_exposure_queue.get()
                    self.window_app.change_displayed_img_raw(image)
                    self.window_app.print_on_console("Stopping raster ... done!")
                    return
                
                comment_string = "SimpleRaster(" + str(col) + "," + str(row) + ")"
                
                if self.is_continuous or self.exposure_time < 16000:
                    #raw_image,_,_ = bsf.laueClient("192.168.1.10",50000,"GetImage\n", True)
                    self.window_app.change_displayed_img_raw(image)
                    cv2.imwrite(saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", image)
                    if isAllowedToSubtractBg:
                        if isAllowedToDetectCenter:
                            bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row, center_detect_queue = self.center_detection_queue, center_detect_save_dir=saveDirectoryCenterDetection, center_detect_bmp_save_dir=saveDirectoryCenterDetectionOptimizedContrastBmp)
                            bgRemoveForSave_thread.start()
                        else:
                            bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row)
                            bgRemoveForSave_thread.start()
                    elif isAllowedToDetectCenter:
                        self.center_detection_queue.put((saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", saveDirectoryCenterDetection))
                
                else:
                    self.window_app.change_displayed_img_raw(image)
                    cv2.imwrite(saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", image)
                    if isAllowedToSubtractBg:
                        if isAllowedToDetectCenter:
                            bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row, center_detect_queue = self.center_detection_queue, center_detect_save_dir=saveDirectoryCenterDetection, center_detect_bmp_save_dir=saveDirectoryCenterDetectionOptimizedContrastBmp)
                            bgRemoveForSave_thread.start()
                        else:
                            bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row)
                            bgRemoveForSave_thread.start()
                    elif isAllowedToDetectCenter:
                        self.center_detection_queue.put((saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", saveDirectoryCenterDetection))
                
                #TODO: schauen ob sinnvoll
                if self.is_continuous:
                    img_cache = np.copy(image)
                    min_value = int(np.min(img_cache))
                    max_value = int(np.max(img_cache))
                    mean_to_scale=70
                    
                    for j in range(min_value+1, max_value+1):
                        image_cache = (255.0/(float(j) - float(min_value))) * np.subtract(img_cache, min_value)
                        image_cache[image_cache < 0.0] = 0.0
                        image_cache[image_cache > 255.0] = 255.0
                        mean = np.mean(image_cache)
                        if np.abs(mean-mean_to_scale) < 0.5:
                            break
                    gray = np.copy(img_cache).astype('uint8')
                else:    
                    #Reduce dynamic Range to 8 bit
                    gray = (image/256).astype('uint8')
                
                
                #Find the Dots and save a copy of each analysis
                
                mD, sD, current_image = bsf.maxFinder_large(gray, saveDirectory, True , False, comment_string,-3, int(self.exposure_time/1000), filelist=self.filelist)
                
                #Get and save the image parameters
                result[col,row] = len(mD) + len(sD)
                stddev[col,row], _ = cv2.meanStdDev(gray)
                avg[col,row] = scaleMean
                
                #set this tile to the "scanned but nothing found" status.
                #if something is found later on, this will be overwritten.
                treffer[col,row] = 0
                
                #Debug output for setting the apropriate sddev levels
                print("Bright: " + str(stddev[col,row]))
                
                if self.exposure_time <= 5000:
                    if stddev[col,row] < stddev_comparison_array[0][aperture_value - 1]:
                        treffer[col,row] = 2
                elif self.exposure_time <= 10000:
                    if stddev[col,row] < stddev_comparison_array[1][aperture_value - 1]: #Maximalwert für TiO auf Alu: 160
                        treffer[col,row] = 2
                elif self.exposure_time <= 16000:
                    if stddev[col,row] < stddev_comparison_array[2][aperture_value - 1]:
                        treffer[col,row] = 2
                else:
                    if stddev[col,row] < sddev_longexposure_value[aperture_value - 1]:
                        treffer[col,row] = 2
                
                #self.window_app.plot_array(treffer)
                #self.window_app.plot.draw()
                self.request_kontur_queue.put(treffer)
                self.request_cur_det_max_queue.put(current_image)
                #Draw the current progress for the user
                bsf.showPlotImage(treffer, "Scan" , current_image, "Aktuelles Bild")
                
        
        #if the exposure time is reasonably long, use the dot-search to determine the center of the picture
        if self.exposure_time > minimum_time_for_dotsearch:
            #print("Punktsucher:")
            #print(result)
            counter = 0.0;
            avgDotnumber = 0.0;
            
            for col in range(result.shape[0]):
                for row in range(result.shape[1]):
                    #if  stddev[col,row] > 160:
                    if treffer[col,row] != 2:
                        result[col,row] = 0
                    else:
                        counter += 1
                        avgDotnumber += result[col,row]
                        
            if counter > 0:
                avgDotnumber = avgDotnumber / counter
                #print("Average Dotnumber in low stdev Areas: " + str(avgDotnumber))
                        
            for col in range(result.shape[0]):
                for row in range(result.shape[1]):
                    #if result[col,row] < avgDotnumber and result[col,row] > 0:
                    if result[col,row] > avgDotnumber:
                        treffer[col,row] = 3
        else:
            print("Short exposure time, only using stddev. This can lead to false negatives!")
        
        #show general stats
        print("Done, result:")
        print(treffer)
        #print(np.average(result))    
        #print("Mean:")
        #print(avg)
        #print("stddev:")
        #print(stddev)
        """
        if not(stop_exposure_queue.empty()):
            stop_exposure_queue.get()
            self.window_app.change_displayed_img_raw(image)
            self.window_app.print_on_console("Stopping raster ... done!")
            return
        """
        #find the center of the contour
        print("Suche das Zentrum der Konturen:")
        bsf.showPlot(treffer, "Kontur")
        
        path = saveDirectory + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + "logfile.txt"
        logfile = "hight:" + str(self.hight) + ":width:" + str(self.width) + ":scale:" + str(self.scale) + ":exposureTime:" + str(self.exposure_time/1000) + ":coordinates:(" + str(self.coordinates[1]) + ", " + str(-1 * self.coordinates[0]) + "):"
        if(self.is_continuous):
            logfile = logfile + "continuous:1:\n#"
        else:
            logfile = logfile + "additive:0:\n#"
        text = str(treffer)
        with open(path, 'w') as f:
            f.write(logfile + text)
        with open(saveDirectoryOrginal + "/logfile.txt", 'w') as f:
            f.write(logfile + text)
        if isAllowedToSubtractBg:
            with open(saveDirectoryOrginalBgRemoved + "/logfile.txt", 'w') as f:
                f.write(logfile + text)
        elif isAllowedToDetectCenter:
            self.center_detection_queue.put(("Stop", saveDirectoryCenterDetectionWholeResults, path, saveDirectoryOrginal + "/logfile.txt"))
                
        
        
        self.request_kontur_queue.put(treffer)
        self.window_app.current_kontur_array = np.copy(treffer)
        self.window_app.current_kontur_shape = np.shape(treffer)
        self.window_app.current_kontur_offset = offset
        self.window_app.current_kontur_scale = self.scale
        answer = bsf.findCenter(treffer)
        
        #print(answer)
        #print(len(answer[0]))
        #print(len(answer[1]))
        #print(result.shape)
        
        if len(answer[1]) > 0:
            print("Maxlocation X: " + str((answer[1][0][0] - (result.shape[1]-1)/2.0)*self.scale + offset[1]))
            print("Maxlocation Y: " + str((answer[1][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            
            #Move to the approximate center of the contour
            bsf.motorClient('M', 'Y', -((answer[1][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1])
            bsf.motorClient('M', 'X', (answer[1][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0])
            self.window_app.print_on_console("Maxlocation X: " + str((answer[1][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            self.window_app.print_on_console("Maxlocation Y: " + str(-((answer[1][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1]))
            print("Moving the to the center of the contour... done")
            self.window_app.print_on_console("Moving the sample to the center of the contour... done")
            print("You may now take a long exposure image")
            self.window_app.print_on_console("You may now take a long exposure image")
            
            if isAllowedToDetectCenter:
                if isAllowedToSubtractBg:
                    time.sleep(25)
                    self.center_detection_queue.put(("Stop", saveDirectoryCenterDetectionWholeResults, path, saveDirectoryOrginal + "/logfile.txt",saveDirectoryOrginalBgRemoved + "/logfile.txt"))
            return
        
        
        if len(answer[0]) > 0:
            #print(str(answer[0][0]) + " " + str(answer[0][1]))
            #print(answer[0][0])
            print("Maxlocation X: " + str((answer[0][0][0] - (result.shape[1]-1)/2.0)*self.scale + offset[1]))
            print("Maxlocation Y: " + str((answer[0][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            
            #Move to the approximate center of the contour
            bsf.motorClient('M', 'Y', -((answer[0][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1])
            bsf.motorClient('M', 'X', (answer[0][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0])
            self.window_app.print_on_console("Maxlocation X: " + str((answer[0][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            self.window_app.print_on_console("Maxlocation Y: " + str(-((answer[0][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1]))
            print("Moving the sample to the center of the contour... done")
            self.window_app.print_on_console("Moving the sample to the center of the contour... done")
            print("You may now take a long exposure image")
            self.window_app.print_on_console("You may now take a long exposure image")
            if isAllowedToDetectCenter:
                if isAllowedToSubtractBg:
                    time.sleep(25)
                    self.center_detection_queue.put(("Stop", saveDirectoryCenterDetectionWholeResults, path, saveDirectoryOrginal + "/logfile.txt",saveDirectoryOrginalBgRemoved + "/logfile.txt"))
            return
        
        print("[Error] No contour has been identified!")
        self.window_app.print_on_console("[Error] No contour has been identified!")
        bsf.home()
        
    def check_save_directory(self, num=0):
        if num == 0:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
                return 
            else:
                self.check_save_directory(2)
        else:
            if not os.path.exists(self.save_directory + "_" + str(num)):
                os.makedirs(self.save_directory + "_" + str(num))
                self.save_directory = self.save_directory + "_" + str(num)
                return 
            else:
                self.check_save_directory(num + 1)
     
    def prepare_image_for_maxFinder(self, final_picture):
        ny = 643
        nx = 975
        x_start = int(final_picture.shape[1]/2)-50-int(0.059*ny + 1)
        x_stop = int(final_picture.shape[1]/2)-int(0.059*ny + 1)
        y_start = int(final_picture.shape[0]/2)-50-int(0.059*ny + 1)
        y_stop = int(final_picture.shape[0]/2)-int(0.059*ny + 1)
        
        crop_img = final_picture[y_start:y_stop,x_start:x_stop]
        
        mean,_ = cv2.meanStdDev(crop_img)
        cv2.circle(final_picture, (int(nx/2) + 4,int(ny/2) + 4), int(0.054*ny+1), (mean[0][0],mean[0][0],mean[0][0]), -1)
        
        #Get the extreme luminance values and increase contrast so that the
        #   entire histogram is used (in order to not loose too much detail 
        #   when converting to 8-bit)
        minValue, maxValue,_,_ = cv2.minMaxLoc(final_picture)
        globalMin = np.ones(final_picture.shape)
        globalMin = globalMin * minValue
        final_picture = np.subtract(final_picture, globalMin)
        final_picture = final_picture * int(65535/(maxValue-minValue))
        return final_picture

    
class AsyncKonturDetection(Thread):
    def __init__(self, origin, stepsize, minimum_dots, maximum_dots, maximum_mean, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, window_app):
        super().__init__()
        self.origin = origin
        self.stepsize = stepsize
        self.minimum_dots = minimum_dots
        self.maximum_mean = maximum_mean
        self.maximum_dots = maximum_dots
        self.solution = []
        self.stop_exposure_queue = stop_exposure_queue
        self.request_kontur_queue = request_kontur_queue
        self.request_cur_det_max_queue = request_cur_det_max_queue
        self.window_app = window_app
        self.kontur = np.ones((1,1)) * 2
        self.help_var = 0
        
    def run(self):
        #TODO: cancel methode hinzufügen
        self.kontur[0][0] = 1
        self.request_kontur_queue.put(self.kontur)
        positive_y = self.first_step(self.origin, self.stepsize, (1,0), self.kontur)
        self.help_var = positive_y
        negative_y = self.first_step(self.origin, self.stepsize, (-1,0), self.kontur)
        positive_x = self.first_step(self.origin, self.stepsize, (0,1), self.kontur)
        negative_x = self.first_step(self.origin, self.stepsize, (0,-1), self.kontur)
        print("positive x: " + str(positive_x))
        print("positive y: " + str(positive_y))
        print("negative x: " + str(negative_x))
        print("negative y: " + str(negative_y))
        
        answ = self.vertical_linescan(self.origin[0], self.origin[1] + negative_x * self.stepsize, self.stepsize, positive_y, negative_y)
        """if answ - self.origin[0])//self.stepsize == 0:
           negative_x = abs((answ - self.origin[1])//self.stepsize)"""
        negative_x = int(np.abs((answ - self.origin[1])//self.stepsize))
        print("answer vertical_linescan negative_x: " +  str(answ))   
        print("negative x: " + str(negative_x))
        
        answ = self.vertical_linescan(self.origin[0], self.origin[1] - positive_x * self.stepsize, self.stepsize, positive_y, negative_y)
        """if not(answ == None):
           positive_x = abs((answ - self.origin[1])//self.stepsize)""" 
        positive_x = int(np.abs((answ - self.origin[1])//self.stepsize))
        print("answer vertical_linescan positive_x: " +  str(answ))
        print("positive x: " + str(positive_x))
        
        answ = self.horizontal_linescan(self.origin[0] + negative_y * self.stepsize, self.origin[1], self.stepsize, positive_x, negative_x)
        """if not(answ == None):
           negative_y = abs((answ - self.origin[0])//self.stepsize)"""
        negative_y = int(np.abs((answ - self.origin[0])//self.stepsize))
        print("answer horizontal_linescan negative_y: " +  str(answ))
        print("negative y: " + str(negative_y))
        
        answ = self.horizontal_linescan(self.origin[0] - positive_y * self.stepsize, self.origin[1], self.stepsize, positive_x, negative_x)
        """if not(answ == None):
           positive_y = abs((answ - self.origin[0])//self.stepsize)"""
        positive_y = int(np.abs((answ - self.origin[0])//self.stepsize))
        print("answer horizontal_linescan positive_y: " +  str(answ))
        print("positive y: " + str(positive_y))
        
        print("final positive x: " + str(positive_x))
        print("final negative x: " + str(negative_x))
        print("final positive y: " + str(positive_y))
        print("final negative y: " + str(negative_y))
        
        center_x = ((negative_y - positive_y)/2)* self.stepsize + self.origin[0]
        center_y = ((negative_x - positive_x)/2)* self.stepsize + self.origin[1]
        """
        if int(negative_y + positive_y) % 2:
            h = int(positive_y + negative_y + 1)
        else:
            h = int(positive_y + negative_y)
            
        if int(negative_x + positive_y) % 2:
            w = int(positive_x + negative_x)
        else:
            w = int(positive_x + negative_x)
        """
        h = int(positive_y + negative_y + 1)
        w = int(positive_x + negative_x + 1)
        
        self.solution.append(center_x)
        self.solution.append(center_y)
        self.solution.append(h)
        self.solution.append(w)
        
        print("center_x: " + str(center_x))
        print("center_y: " + str(center_y))
        print("h: " + str(h))
        print("w: " + str(w))
        
        
        
    def first_step(self, origin, stepsize, direction, kontur):
        no_hit = False
        i = 1
        while no_hit == False:
            add_i = 2
            bsf.motorClient('M', 'X', origin[0] - direction[0] * i * self.stepsize)
            bsf.motorClient('M', 'Y', origin[1] - direction[1] * i * self.stepsize)
            
            if not(self.expose_image()):
                no_hit = True
                add_i = 0
            else:
                i = i + 1
                
            if direction[0] == 1:
                add_arr = [[add_i]]
                self.kontur = np.concatenate((add_arr, self.kontur), axis=0)
            elif direction[0] == -1:
                add_arr = [[add_i]]
                self.kontur = np.concatenate((self.kontur, add_arr), axis=0)
            elif direction[1] == 1:
                add_arr = np.zeros((np.shape(self.kontur)[0],1))
                add_arr[self.help_var][0] = add_i
                self.kontur = np.concatenate((self.kontur, add_arr), axis=1)
            elif direction[1] == -1:
                add_arr = np.zeros((np.shape(self.kontur)[0],1))
                add_arr[self.help_var][0] = add_i
                self.kontur = np.concatenate((add_arr, self.kontur), axis=1)
            self.request_kontur_queue.put(self.kontur)   
 
        return i
    """
    def vertical_linescan(self, x0, y0, stepsize, up, down):
        bsf.motorClient('M','Y', y0)
        for i in range(-down, up + 1):
            if (y0 - self.origin[1]) > 0:
                self.kontur[-(i+down+1)][0] = 3
            else:
                self.kontur[-(i+down+1)][-1] = 3
            self.request_kontur_queue.put(self.kontur)
            
            bsf.motorClient('M', 'X', x0 - i * self.stepsize)
            
            if self.expose_image():
                if (y0 - self.origin[1]) > 0:
                    direction = 1
                    add_arr = np.zeros((np.shape(self.kontur)[0],1))
                    self.kontur[-(i+down+1)][0] = 2
                    self.kontur = np.concatenate((add_arr, self.kontur), axis=1)
                else:
                    direction = -1
                    add_arr = np.zeros((np.shape(self.kontur)[0],1))
                    self.kontur[-(i+down+1)][-1] = 2
                    self.kontur = np.concatenate((self.kontur, add_arr), axis=1)
                self.vertical_linescan(x0, y0 + stepsize * direction, stepsize, up, -i)
            else:
                if (y0 - self.origin[1]) > 0:
                    self.kontur[-(i+down+1)][0] = 1
                else:
                    self.kontur[-(i+down+1)][-1] = 1
        return y0
    """
    def vertical_linescan(self, x0, y0, stepsize, up, down):
        bsf.motorClient('M','Y', y0)
        for i in range(-down, up + 1):
            if (y0 - self.origin[1]) > 0:
                self.kontur[up - i][0] = 3
            else:
                self.kontur[up - i][-1] = 3
            self.request_kontur_queue.put(self.kontur)
            
            bsf.motorClient('M', 'X', x0 - i * self.stepsize)
            
            if self.expose_image():
                if (y0 - self.origin[1]) > 0:
                    direction = 1
                    add_arr = np.zeros((np.shape(self.kontur)[0],1))
                    self.kontur[up - i][0] = 2
                    self.kontur = np.concatenate((add_arr, self.kontur), axis=1)
                else:
                    direction = -1
                    add_arr = np.zeros((np.shape(self.kontur)[0],1))
                    self.kontur[up - i][-1] = 2
                    self.kontur = np.concatenate((self.kontur, add_arr), axis=1)
                y0 = self.vertical_linescan(x0, y0 + stepsize * direction, stepsize, up, -i)
                break
            else:
                if (y0 - self.origin[1]) > 0:
                    self.kontur[up - i][0] = 1
                else:
                    self.kontur[up - i][-1] = 1
        return y0
    """
    def horizontal_linescan(self, x0, y0, stepsize, right, left):
        bsf.motorClient('M','X', x0)
        for i in range(-left, right + 1):
            if (x0 - self.origin[0]) > 0:
                self.kontur[-1][i+left] = 3
            else:
                self.kontur[0][i+left] = 3
            self.request_kontur_queue.put(self.kontur)    
            
            bsf.motorClient('M', 'Y', y0 - i * self.stepsize)
            if self.expose_image():
                if (x0 - self.origin[0]) > 0:
                    direction = 1
                    add_arr = np.zeros((1,np.shape(self.kontur)[0]))
                    self.kontur[-1][i+left] = 2
                    self.kontur = np.concatenate((self.kontur, add_arr), axis=0)
                else:
                    direction = -1
                    add_arr = np.zeros((1,np.shape(self.kontur)[0]))
                    self.kontur[0][i+left] = 2
                    self.kontur = np.concatenate((add_arr, self.kontur), axis=0)
                self.request_kontur_queue.put(self.kontur)
                self.vertical_linescan(x0 + stepsize * direction, y0, stepsize, right, -i)
            else:
                if (x0 - self.origin[0]) > 0:
                    self.kontur[-1][i+left] = 1
                else:
                    self.kontur[0][i+left] = 1
                self.request_kontur_queue.put(self.kontur)
        return x0
    """   
    def horizontal_linescan(self, x0, y0, stepsize, right, left):
        #TODO: schauen ob horizontal_linescan richtig visualisiert wird
        bsf.motorClient('M','X', x0)
        for i in range(-left, right + 1):
            if (x0 - self.origin[0]) > 0:
                self.kontur[-1][-(right+1-i)] = 3
            else:
                self.kontur[0][-(right+1-i)] = 3
            self.request_kontur_queue.put(self.kontur)    
            
            bsf.motorClient('M', 'Y', y0 - i * self.stepsize)
            if self.expose_image():
                if (x0 - self.origin[0]) > 0:
                    direction = 1
                    add_arr = np.zeros((1,np.shape(self.kontur)[1]))
                    self.kontur[-1][-(right+1-i)] = 2
                    self.kontur = np.concatenate((self.kontur, add_arr), axis=0)
                else:
                    direction = -1
                    add_arr = np.zeros((1,np.shape(self.kontur)[1]))
                    self.kontur[0][-(right+1-i)] = 2
                    self.kontur = np.concatenate((add_arr, self.kontur), axis=0)
                self.request_kontur_queue.put(self.kontur)
                x0 = self.vertical_linescan(x0 + stepsize * direction, y0, stepsize, right, -i)
                break
            else:
                if (x0 - self.origin[0]) > 0:
                    self.kontur[-1][-(right+1-i)] = 1
                else:
                    self.kontur[0][-(right+1-i)] = 1
                self.request_kontur_queue.put(self.kontur)
        return x0
    
    def expose_image(self):
        image = bsf.longExposure(31, self.stop_exposure_queue)
        self.window_app.change_displayed_img_raw(image)
        gray = (image/256).astype('uint8')
        mD, sD, cimage = bsf.maxFinder_large(gray, None)
        self.request_cur_det_max_queue.put(cimage)
        all_dots = len(mD) + len(sD)
        mean = cv2.meanStdDev(gray)[0]
        
        self.window_app.print_on_console("number of dots: " + str(all_dots) + ", mean: " + str(round(cv2.meanStdDev(gray)[0][0][0],2)))
        #print("mean: " + str(cv2.meanStdDev(gray)[0]))
        #print("StdDev: " + str(cv2.meanStdDev(gray)[1]))
        if all_dots < self.minimum_dots or all_dots > self.maximum_dots or mean > self.maximum_mean:
            return False
        return True
    
def AcquireKontur(shape, origin, stepsize, stop_exposure_queue):
    kontur = np.zeros(shape)
    for col in range(kontur.shape[0]):
        #Move in x-axis
        print("move x:")
        xpos = (col - (kontur.shape[0]-1)/2.0)*stepsize + origin[0]
        bsf.motorClient('M', 'X', xpos)
        
        for row in range(kontur.shape[1]):
                            
            #Move in y-axis
            print("move y:")
            ypos = ((kontur.shape[1]-1)/2.0 - row)*stepsize + origin[1]
            bsf.motorClient('M', 'Y', ypos)
        
            image = bsf.longExposure(31, stop_exposure_queue)
            gray = (image/256).astype('uint8')
            mD, sD, _ = bsf.maxFinder_large(gray, None)
            all_dots = len(mD) + len(sD)
            mean = cv2.meanStdDev(gray)[0]
            print("all dots: " + str(all_dots))
            print("mean: " + str(cv2.meanStdDev(gray)[0]))
            print("StdDev: " + str(cv2.meanStdDev(gray)[1]))
            if all_dots < 1 or all_dots > 150 or mean > 185.0:
                kontur[col,row] = 1
            else:
                kontur[col,row] = 2
                
    print(kontur - 1)
    return (kontur - 1)
        
 
#TODO: anpassen auf heatmap und überlegen wie darstellen wenn neben der kontur
class AsyncKonturRaster(Thread):
    def __init__(self, hight, width, scale, exposure_time,y0,x0, window_app, stop_exposure_queue, request_kontur_queue, request_cur_det_max_queue, center_detection_queue, is_continuous = False):
        super().__init__()
        self.hight = hight
        self.width = width
        self.scale = scale
        self.exposure_time = exposure_time * 1000
        self.coordinates = (y0,x0)
        self.window_app = window_app
        self.filelist = []
        self.is_continuous = is_continuous
        self.save_directory = window_app.save_directory
        self.stop_exposure_queue = stop_exposure_queue
        self.request_kontur_queue = request_kontur_queue
        self.request_cur_det_max_queue = request_cur_det_max_queue
        self.center_detection_queue = center_detection_queue
        

    def run(self):

        #initial constants
        minimum_time_for_dotsearch = 4999  #in ms of exposure
        aperture_value = 2  #number written onto the X-Ray aperture
        #exposure_time = 5000
        
        #calibration array [stage][aperture_value] = data
        stddev_comparison_array = np.array([[175, 145, 105, 0],
                                            [170, 130, 110, 0],
                                            [162, 120, 90, 0],
                                            [0, 0, 0, 0]])
        
        #similar to stddev_comparison_array but for long exposures
        sddev_longexposure_value = np.array([190,185,190,100])
        
        print(stddev_comparison_array[2][aperture_value - 1])
        offset = (self.coordinates[1], -self.coordinates[0])
        
        #initialie the containers
        result = np.zeros((self.hight, self.width))
        stddev = np.zeros(result.shape)
        avg = np.zeros(result.shape)
        treffer = np.ones(result.shape, np.uint8)
        
        #timing calculations
        #TODO: noch anpassen generell aber vor allem auf max_exposure Bestimmung
        #TODO: duration auf raster schätzen anpassen
        if self.exposure_time <= 16000:
            bsf.setExposure(self.exposure_time)
        
        duration = 0.0
        if self.is_continuous:
            if(self.exposure_time/1000 < 90):
                duration = result.shape[0] * result.shape[1] * (self.exposure_time + 2000)
            elif self.window_app.settings_calculate_max_exposure_during_raster.get() and (self.exposure_time/1000 > 90):
                duration = result.shape[0] * result.shape[1] * (self.exposure_time + 6000 + 30000)
            else:
                duration = result.shape[0] * result.shape[1] * (((self.window_app.max_exposure + 2000)*self.exposure_time//self.window_app.max_exposure) + self.exposure_time%self.window_app.max_exposure + 2000)
        else:
            duration = result.shape[0] * result.shape[1] * (18000*(self.exposure_time//16000) + (self.exposure_time%16000 + 2000))
        seconds = duration/1000
        days = int(seconds/86400)
        hours = int((seconds%86400)/3600)
        minutes = int((seconds%3600)/60)
        sec = int((seconds%60))
        
        print("Approximate duration: " + str(days) + "days, " + str(hours) + "h, " + str(minutes) + "min, " + str(sec) + "sec")
        self.window_app.print_on_console("Approximate raster duration: " + str(days) + "days, " + str(hours) + "h, " + str(minutes) + "min, " + str(sec) + "sec")
        
        now = dt.datetime.now()
        time_necessary = dt.timedelta(days = days, hours = hours, minutes = minutes, seconds = sec )
        finish = now + time_necessary
        string = "%02d-%02d %02d:%02d" % (finish.day, finish.month, finish.hour, finish.minute)
        self.window_app.print_on_console("Approximate finish: " + string)
        
        #create save directory
        
        ordner_name = self.window_app.settings_file_prefix + "_RASTER_" + str(int(self.exposure_time/1000)) + "s_" + str(self.width) + "x" + str(self.hight) + "_" + str(self.scale) + "mm"
        
        self.save_directory = self.save_directory + "/" + ordner_name
        
        if(self.is_continuous):
            self.save_directory = self.save_directory + "_continuous"
        else:
            self.save_directory = self.save_directory + "_additive"
        
        self.check_save_directory()
        saveDirectory =  self.save_directory + "/"
        saveDirectoryOrginal = self.save_directory + "/Original_Pictures"
        os.makedirs(saveDirectoryOrginal)
        isAllowedToSubtractBg = False
        isAllowedToCaluclateMaxExposure = self.window_app.settings_calculate_max_exposure_during_raster.get()
        only12BitImage = self.window_app.settings_12_bit_exposure.get()
        
        if (self.window_app.settings_bgRemove_during_raster.get() and ((self.exposure_time/1000) > 59.9)):
            saveDirectoryOrginalBgRemoved = self.save_directory + "/Original_Pictures_Bg_Removed"
            os.makedirs(saveDirectoryOrginalBgRemoved)
            isAllowedToSubtractBg = True
            
        isAllowedToDetectCenter = False
        if (self.window_app.settings_center_detection_during_raster.get()):
            isAllowedToDetectCenter = True
            saveDirectoryCenterDetection = self.save_directory + "/Center_Detection_Results/"
            os.makedirs(saveDirectoryCenterDetection)
            saveDirectoryCenterDetectionWholeResults = self.save_directory + "/Center_Detection_Results/whole_results/"
            os.makedirs(saveDirectoryCenterDetectionWholeResults)
            if isAllowedToSubtractBg:
                saveDirectoryCenterDetectionOptimizedContrastBmp = self.save_directory + "/Center_Detection_Results/bmp_optimized_contrast/"
                os.makedirs(saveDirectoryCenterDetectionOptimizedContrastBmp)
            if (self.window_app.settings_center_detection_save_info_images_raster.get()):
                saveDirectoryCenterDetectionInfoImages = self.save_directory + "/Center_Detection_Results/info_images/"
                os.makedirs(saveDirectoryCenterDetectionInfoImages)
        
        kontur = AcquireKontur(result.shape, offset, self.scale, self.stop_exposure_queue)
        
        for col in range(result.shape[0]):
            
            #Move in x-axis
            #print(str((col - (result.shape[0]-1)/2.0)*scale) + str(offset[0]) + " = " + str((col - (result.shape[0]-1)/2.0)*scale + offset[0]))
            print("move x:")
            xpos = (col - (result.shape[0]-1)/2.0)*self.scale + offset[0]
            bsf.motorClient('M', 'X', xpos)
            
            for row in range(result.shape[1]):
                if kontur[col,row] == 1:                
                    #Move in y-axis
                    print("move y:")
                    ypos = ((result.shape[1]-1)/2.0 - row)*self.scale + offset[1]
                    bsf.motorClient('M', 'Y', ypos)
                    
                    #Take the picture
                    if self.is_continuous:
                        if not(only12BitImage):
                            if(self.exposure_time/1000 < 90):
                                image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, int(self.exposure_time/1000), True)
                            elif isAllowedToCaluclateMaxExposure and (self.exposure_time/1000 > 90):
                                return_image = bsf.longSecondExposure(30, self.stop_exposure_queue, 31, True)
                                self.window_app.max_exposure = int(114000/(np.max(return_image) - 100))
                                image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, self.window_app.max_exposure, True)
                            else:
                                image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, self.window_app.max_exposure, True)
                        else:
                            image = bsf.longSecondExposure(int(self.exposure_time/1000), self.stop_exposure_queue, self.window_app.max_exposure_PSL_Viewer)
                        scaleMean, scaleStddev = cv2.meanStdDev(image)
                    
                    else:
                        if self.exposure_time > 16000:
                            image = bsf.longExposure(self.exposure_time/1000, self.stop_exposure_queue)
                            scaleMean, scaleStddev = cv2.meanStdDev(image)
                            
                        else:
                            bsf.tC("192.168.1.10", 50000, "Snap\n")
                            for i in range(int(self.exposure_time/1000) + 1):
                                if not(self.stop_exposure_queue.empty()):
                                    bsf.tC("192.168.1.10", 50000, "Stop\n")
                                    return_array = (127 * np.ones((643,975)))
                                    return_array[0][0] = 0
                                    return_array[1][0] = 255
                                    image = return_array
                                time.sleep(1) 
                            image, rawMean, rawStddev, scaleMean, scaleStddev = bsf.laueClient("192.168.1.10",50000,"GetImage\n")
                            #print("RawMean, RawStddev, sMean, sStddev: " + str(rawMean) + " " + str(rawStddev) + " " + str(scaleMean) + " " + str(scaleStddev) + " ")
                    
                    if not(self.stop_exposure_queue.empty()):
                        self.stop_exposure_queue.get()
                        self.window_app.change_displayed_img_raw(image)
                        self.window_app.print_on_console("Stopping raster ... done!")
                        return
                    
                    comment_string = "SimpleRaster(" + str(col) + "," + str(row) + ")"
                    
                    if self.is_continuous or self.exposure_time < 16000:
                        #raw_image,_,_ = bsf.laueClient("192.168.1.10",50000,"GetImage\n", True)
                        self.window_app.change_displayed_img_raw(image)
                        cv2.imwrite(saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", image)
                        if isAllowedToSubtractBg:
                            if isAllowedToDetectCenter:
                                bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row, center_detect_queue = self.center_detection_queue, center_detect_save_dir=saveDirectoryCenterDetection, center_detect_bmp_save_dir=saveDirectoryCenterDetectionOptimizedContrastBmp)
                                bgRemoveForSave_thread.start()
                            else:
                                bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row)
                                bgRemoveForSave_thread.start()
                        elif isAllowedToDetectCenter:
                            self.center_detection_queue.put((saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", saveDirectoryCenterDetection))
                    
                    else:
                        self.window_app.change_displayed_img_raw(image)
                        cv2.imwrite(saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", image)
                        if isAllowedToSubtractBg:
                            if isAllowedToDetectCenter:
                                bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row, center_detect_queue = self.center_detection_queue, center_detect_save_dir=saveDirectoryCenterDetection, center_detect_bmp_save_dir=saveDirectoryCenterDetectionOptimizedContrastBmp)
                                bgRemoveForSave_thread.start()
                            else:
                                bgRemoveForSave_thread = abf.AsyncBgRemoveForSave(image, saveDirectoryOrginalBgRemoved, str(int(self.exposure_time/1000)) + "s_" + comment_string, self.window_app, col, row)
                                bgRemoveForSave_thread.start()
                        elif isAllowedToDetectCenter:
                            self.center_detection_queue.put((saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", saveDirectoryCenterDetection))
                    
                    #TODO: überarbeiten
                    #if self.is_continuous:
                    #    image = self.prepare_image_for_maxFinder(image)
                        
                    #Reduce dynamic Range to 8 bit
                    gray = (image/256).astype('uint8')
                
                    #Find the Dots and save a copy of each analysis
                    
                    mD, sD, current_image = bsf.maxFinder_large(gray, saveDirectory, True , False, comment_string,-3, int(self.exposure_time/1000), filelist=self.filelist)
                    
                    #Get and save the image parameters
                    result[col,row] = len(mD) + len(sD)
                    stddev[col,row], _ = cv2.meanStdDev(gray)
                    avg[col,row] = scaleMean
                    
                    #set this tile to the "scanned but nothing found" status.
                    #if something is found later on, this will be overwritten.
                    treffer[col,row] = 0
                    
                    #Debug output for setting the apropriate sddev levels
                    print("Bright: " + str(stddev[col,row]))
                    
                    if self.exposure_time <= 5000:
                        if stddev[col,row] < stddev_comparison_array[0][aperture_value - 1]:
                            treffer[col,row] = 2
                    elif self.exposure_time <= 10000:
                        if stddev[col,row] < stddev_comparison_array[1][aperture_value - 1]: #Maximalwert für TiO auf Alu: 160
                            treffer[col,row] = 2
                    elif self.exposure_time <= 16000:
                        if stddev[col,row] < stddev_comparison_array[2][aperture_value - 1]:
                            treffer[col,row] = 2
                    else:
                        if stddev[col,row] < sddev_longexposure_value[aperture_value - 1]:
                            treffer[col,row] = 2
                
                else:
                    image = 127 * np.ones((643,975))
                    image[0][0] = 0
                    image[1][0] = 255
                    gray = (image/256).astype('uint8')
                    comment_string = "SimpleRaster(" + str(col) + "," + str(row) + ")"
                    bsf.maxFinder_large(gray, saveDirectory, True , False, comment_string,-3, int(self.exposure_time/1000), filelist=self.filelist)
                    current_image = np.copy(gray)
                    cv2.imwrite(saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", current_image)
                    if isAllowedToDetectCenter:
                        self.center_detection_queue.put((saveDirectoryOrginal + "/" + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + str(int(self.exposure_time/1000)) + "s_" + comment_string + ".tif", saveDirectoryCenterDetection))
                    treffer[col,row] = 0
                
                #self.window_app.plot_array(treffer)
                #self.window_app.plot.draw()
                self.request_kontur_queue.put(treffer)
                self.request_cur_det_max_queue.put(current_image)
                #Draw the current progress for the user
                bsf.showPlotImage(treffer, "Scan" , current_image, "Aktuelles Bild")                    
        
        #if the exposure time is reasonably long, use the dot-search to determine the center of the picture
        if self.exposure_time > minimum_time_for_dotsearch:
            #print("Punktsucher:")
            #print(result)
            counter = 0.0;
            avgDotnumber = 0.0;
            
            for col in range(result.shape[0]):
                for row in range(result.shape[1]):
                    #if  stddev[col,row] > 160:
                    if treffer[col,row] != 2:
                        result[col,row] = 0
                    else:
                        counter += 1
                        avgDotnumber += result[col,row]
                        
            if counter > 0:
                avgDotnumber = avgDotnumber / counter
                #print("Average Dotnumber in low stdev Areas: " + str(avgDotnumber))
                        
            for col in range(result.shape[0]):
                for row in range(result.shape[1]):
                    #if result[col,row] < avgDotnumber and result[col,row] > 0:
                    if result[col,row] > avgDotnumber:
                        treffer[col,row] = 3
        else:
            print("Short exposure time, only using stddev. This can lead to false negatives!")
        
        #show general stats
        print("Done, result:")
        print(treffer)
        #print(np.average(result))    
        #print("Mean:")
        #print(avg)
        #print("stddev:")
        #print(stddev)
        """
        if not(stop_exposure_queue.empty()):
            stop_exposure_queue.get()
            self.window_app.change_displayed_img_raw(image)
            self.window_app.print_on_console("Stopping raster ... done!")
            return
        """
        #find the center of the contour
        print("Suche das Zentrum der Konturen:")
        bsf.showPlot(treffer, "Kontur")
        
        path = saveDirectory + time.strftime("%Y%m%d%H%M%S", time.gmtime()) + "_" + "logfile.txt"
        logfile = "hight:" + str(self.hight) + ":width:" + str(self.width) + ":scale:" + str(self.scale) + ":exposureTime:" + str(self.exposure_time/1000) + ":coordinates:(" + str(self.coordinates[1]) + ", " + str(-1 * self.coordinates[0]) + "):"
        if(self.is_continuous):
            logfile = logfile + "continuous:1:\n#"
        else:
            logfile = logfile + "additive:0:\n#"
        text = str(treffer)
        with open(path, 'w') as f:
            f.write(logfile + text)
        with open(saveDirectoryOrginal + "/logfile.txt", 'w') as f:
            f.write(logfile + text)
        if isAllowedToSubtractBg:
            with open(saveDirectoryOrginalBgRemoved + "/logfile.txt", 'w') as f:
                f.write(logfile + text)
        elif isAllowedToDetectCenter:
            self.center_detection_queue.put(("Stop", saveDirectoryCenterDetectionWholeResults, path, saveDirectoryOrginal + "/logfile.txt"))
        
        self.request_kontur_queue.put(treffer)
        self.window_app.current_kontur_array = np.copy(treffer)
        self.window_app.current_kontur_shape = np.shape(treffer)
        self.window_app.current_kontur_offset = offset
        self.window_app.current_kontur_scale = self.scale
        answer = bsf.findCenter(treffer)
        
        #print(answer)
        #print(len(answer[0]))
        #print(len(answer[1]))
        #print(result.shape)
        
        if len(answer[1]) > 0:
            print("Maxlocation X: " + str((answer[1][0][0] - (result.shape[1]-1)/2.0)*self.scale + offset[1]))
            print("Maxlocation Y: " + str((answer[1][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            
            #Move to the approximate center of the contour
            bsf.motorClient('M', 'Y', -((answer[1][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1])
            bsf.motorClient('M', 'X', (answer[1][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0])
            self.window_app.print_on_console("Maxlocation X: " + str((answer[1][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            self.window_app.print_on_console("Maxlocation Y: " + str(-((answer[1][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1]))
            print("Moving the to the center of the contour... done")
            self.window_app.print_on_console("Moving the sample to the center of the contour... done")
            print("You may now take a long exposure image")
            self.window_app.print_on_console("You may now take a long exposure image")
            
            if isAllowedToDetectCenter:
                if isAllowedToSubtractBg:
                    time.sleep(25)
                    self.center_detection_queue.put(("Stop", saveDirectoryCenterDetectionWholeResults, path, saveDirectoryOrginal + "/logfile.txt",saveDirectoryOrginalBgRemoved + "/logfile.txt"))
            return
        
        
        if len(answer[0]) > 0:
            #print(str(answer[0][0]) + " " + str(answer[0][1]))
            #print(answer[0][0])
            print("Maxlocation X: " + str((answer[0][0][0] - (result.shape[1]-1)/2.0)*self.scale + offset[1]))
            print("Maxlocation Y: " + str((answer[0][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            
            #Move to the approximate center of the contour
            bsf.motorClient('M', 'Y', -((answer[0][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1])
            bsf.motorClient('M', 'X', (answer[0][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0])
            self.window_app.print_on_console("Maxlocation X: " + str((answer[0][0][1] - (result.shape[0]-1)/2.0)*self.scale + offset[0]))
            self.window_app.print_on_console("Maxlocation Y: " + str(-((answer[0][0][0] - (result.shape[1]-1)/2.0)*self.scale) + offset[1]))
            print("Moving the sample to the center of the contour... done")
            self.window_app.print_on_console("Moving the sample to the center of the contour... done")
            print("You may now take a long exposure image")
            self.window_app.print_on_console("You may now take a long exposure image")
            
            if isAllowedToDetectCenter:
                if isAllowedToSubtractBg:
                    time.sleep(25)
                    self.center_detection_queue.put(("Stop", saveDirectoryCenterDetectionWholeResults, path, saveDirectoryOrginal + "/logfile.txt",saveDirectoryOrginalBgRemoved + "/logfile.txt"))
            return
        
        print("[Error] No contour has been identified!")
        self.window_app.print_on_console("[Error] No contour has been identified!")
        bsf.home()
        
    def check_save_directory(self, num=0):
        if num == 0:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)
                return 
            else:
                self.check_save_directory(2)
        else:
            if not os.path.exists(self.save_directory + "_" + str(num)):
                os.makedirs(self.save_directory + "_" + str(num))
                self.save_directory = self.save_directory + "_" + str(num)
                return 
            else:
                self.check_save_directory(num + 1)
     
    def prepare_image_for_maxFinder(self, final_picture):
        ny = 643
        nx = 975
        x_start = int(final_picture.shape[1]/2)-50-int(0.059*ny + 1)
        x_stop = int(final_picture.shape[1]/2)-int(0.059*ny + 1)
        y_start = int(final_picture.shape[0]/2)-50-int(0.059*ny + 1)
        y_stop = int(final_picture.shape[0]/2)-int(0.059*ny + 1)
        
        crop_img = final_picture[y_start:y_stop,x_start:x_stop]
        
        mean,_ = cv2.meanStdDev(crop_img)
        cv2.circle(final_picture, (int(nx/2) + 4,int(ny/2) + 4), int(0.054*ny+1), (mean[0][0],mean[0][0],mean[0][0]), -1)
        
        #Get the extreme luminance values and increase contrast so that the
        #   entire histogram is used (in order to not loose too much detail 
        #   when converting to 8-bit)
        minValue, maxValue,_,_ = cv2.minMaxLoc(final_picture)
        globalMin = np.ones(final_picture.shape)
        globalMin = globalMin * minValue
        final_picture = np.subtract(final_picture, globalMin)
        final_picture = final_picture * int(65535/(maxValue-minValue))
        return final_picture
          
        
        
        
        
        
        
        
        
        
        
        
    
    