# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 12:32:01 2022

@author: Julian
"""

import numpy as np
from scipy.ndimage.interpolation import rotate, shift
from matplotlib import pyplot as plt
import time
from threading import Thread
import cv2

class ShiftImage(Thread):
    """
    ShiftImage(list_result_rotated, img, height, width, num, deg)
    
    A class for a thread to shift an image realtive to a mask. A rectangle is defined around the center of the mask and the center of the
    image is shifted to each pixel in the area. In each position the image is also rotated 

    Attributes
    ----------
    master: tk-frame
        master of the generated frame 
    number: int
        number of the frame
        
    """
    def __init__(self, list_result_rotated, img, height, width, num, deg):
        super().__init__()
        self.list_result_rotated = list_result_rotated
        self.img = img
        self.height = height
        self.width = width
        self.num = num
        self.side_result = np.zeros((deg, num[1]-num[0]+1, width)) 
        
    def run(self):
        shifted_img = np.zeros(self.img.shape)
        shifted_img[:-self.height//2,:-self.width//2] = self.img[self.height//2+1:,self.width//2+1:]
        for i in range(self.num[0]+1, self.num[1]+2):
            for j in range(1,self.width+1):
                result_shift = np.zeros(self.img.shape)
                result_shift[i:,j:] = shifted_img[:-i,:-j]
                for k in range(len(self.list_result_rotated)):
                    self.side_result[k,i-self.num[0]-1,j-1] = round(np.mean(result_shift[self.list_result_rotated[k] < 1]),1)

class AsyncCenterDetection(Thread):
    def __init__(self, width, height, offset_x, offset_y, linewidth, starting_angle, num_lines, center_coord_P5, rotated_degree, save_info_images, center_detection_queue, window_app):
        super().__init__()
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.linewidth = linewidth
        self.starting_angle = starting_angle
        self.num_lines = num_lines
        self.list_result_rotated = []
        self.center_coord_P5 = center_coord_P5
        self.rotated_degree = rotated_degree
        self.save_info_images = save_info_images
        self.center_detection_queue = center_detection_queue
        self.window_app = window_app
        self.stop_timer_tick = False
        

    def run(self):
        while not(self.center_detection_queue.empty()):
            self.center_detection_queue.get()
        self.calculate_masks()
        self.timertick_center_detection()
        
    def calculate_masks(self):
        # calculate all masks before to enhance runtime
        n,m = (643,975)
        
        arr = np.zeros((n,m), dtype=int)
        big_arr = np.zeros((2*n+1,2*m+1), dtype=int)
        x = m//2
        arr[:,x-self.linewidth:x+self.linewidth+1] = 1
        big_arr[:,2*x-self.linewidth+1:2*x+self.linewidth+2] = 1
        big_arr = np.array(rotate(big_arr, angle=self.starting_angle, reshape=False), dtype=int)
        rotated_big_add = np.copy(big_arr)
        
        # calculate first mask
        for i in range(1,self.num_lines):
            rotated_big = np.array(rotate(big_arr, angle=(180/self.num_lines)*i, reshape=False), dtype=int)
            rotated_big_add = rotated_big_add + rotated_big
        
        x_big = big_arr.shape[1]//2
        y_big = big_arr.shape[0]//2
        
        rotated = rotated_big_add[y_big-n//2:y_big+n//2 + 1, x_big-m//2:x_big+m//2 + 1]
        rotated[rotated > 1] = 1
        
        # calculate the other masks and save them in a list to enhance runtime performance
        
        for k in range(int(180/self.num_lines)):
            result_rotated_big = np.array(rotate(rotated_big_add, angle=k, reshape=False), dtype=int)
            result_rotated = result_rotated_big[y_big-n//2-self.height//2-1:y_big+n//2+self.height//2+ 1, x_big-m//2-self.width//2-1:x_big+m//2+self.width//2 + 1]
            result_rotated[result_rotated > 1] = 1
            
            self.list_result_rotated.append(result_rotated.astype(int))
            
        return
        
#TODO: schauen ob wirklich nach ende auch thread beendet wird bzw diese funktion aufhört
    def timertick_center_detection(self):
        if not(self.center_detection_queue.empty()):
            print("Bild wird bearbeitet")
            element = self.center_detection_queue.get()
            if str(type(element)) == "<class 'tuple'>":
                filename = element[0]
                save_directory = element[1]
                add_list = []
                
                if len(element) > 2:
                    for i in range(len(element)-2):
                        add_list.append(element[i+2])

                if (filename == 'Stop'):
                    if len(element) > 2:
                        self.save_results_and_stop(save_directory, add=add_list)
                    else:
                        self.save_results_and_stop(save_directory)
                    self.stop_timer_tick = True
                    return
                else:                    
                    center, center_P5, rotated_deg = self.detectCenterOfDiffractionPattern(filename, save_directory)
                    self.center_coord_P5[:,len(self.rotated_degree)] = center_P5
                    self.rotated_degree.append(rotated_deg)
                    self.timertick_center_detection()
            else:
                if element == "Stop":
                    self.window_app.print_on_console("Center Detection stopped!")
                else:
                    self.window_app.print_on_console("Wrong data format in async center detection!")
        else:
            if self.stop_timer_tick:
                return
            print("warten")
            self.window_app.raster_button.after(1000, self.timertick_center_detection)
    
#TODO: wenn tif datei dann bmp anpassen
    def detectCenterOfDiffractionPattern(self, filename, save_directory):        
        # define big array to avoid errors by reshaping 
        start = time.time()
        n,m = (643,975)
        degree = int(180/self.num_lines)
        
        # read image
        print(filename)
        img = cv2.imread(filename, -1)
        
        #optimize image contrast for info-image 
        if filename.split("/")[-1][-3:] == "tif" and self.save_info_images:
            img_cache = np.copy(img)
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
            img_original = np.copy(np.array(img_cache, dtype=int)).astype('uint8')
        else:
            img_original = np.copy(np.array(img, dtype=int)).astype('uint8')
        
        # expand image to enhance result after image-shift            
        l_zusatz = np.zeros((n,self.width//2-self.offset_x+1))
        r_zusatz = np.zeros((n,self.width//2+self.offset_x))
        t_zusatz = np.zeros((self.height//2+self.offset_y+1,m+self.width))
        b_zusatz = np.zeros((self.height//2-self.offset_y,m+self.width))
        
        img = np.concatenate((np.concatenate((l_zusatz,img), axis=1),r_zusatz),axis=1)
        img = np.concatenate((np.concatenate((t_zusatz,img), axis=0),b_zusatz), axis=0)
        
        # define result array
        result = np.zeros((degree,self.height,self.width))
        
        # init threads for shorter runtime
        simultan_thread = 4
        threads = []
        for i in range(simultan_thread):
            if i < simultan_thread-1:
                thread = ShiftImage(self.list_result_rotated, img, self.height, self.width, (i*(self.height//simultan_thread),(i+1)*(self.height//simultan_thread)-1), degree)
            else:
                thread = ShiftImage(self.list_result_rotated, img, self.height, self.width, (i*(self.height//simultan_thread),self.height-1), degree)
            thread.start()
            threads.append(thread)
            
        # evaluate the results of the threads
        for index, thread in enumerate(threads):
            thread.join()
            result[:,thread.num[0]:thread.num[1]+1,:] = thread.side_result
            
        
        # mirror the results
        for i in range(result.shape[0]):
            result[i,:,:] = np.fliplr(np.flipud(result[i,:,:]))
        
        # save results
        shape = result.shape
        
        with open(save_directory + filename.split("/")[-1][:-4] + "_result_ShiftImage.txt", 'w') as f:
            for j in range(shape[0]):
                for i in range(shape[1]):
                    string = str(result[j,i,:]).replace("\n", "")
                    f.write(string + "\n")
                f.write("\n")
                
        # evaluate mean of each angle 
        mean = np.zeros((1,degree))
        for i in range(degree):
            mean[0,i] = np.mean(result[i,:,:])
        
        print(mean)
        
        # angel with smallest mean is best orientation
        min_mean = np.where(mean == np.min(mean))[1][0]
        
        # find center of minima of mask with smallest mean
        arr = result[min_mean, :,:]
        arr[arr > np.min(arr)] = 0
        position_minima = np.where(arr == np.max(arr))
        y_center = round(np.mean(position_minima[0]),3)
        x_center = round(np.mean(position_minima[1]),3)
        y_center_toP5 = round(y_center*2)/2
        x_center_toP5 = round(x_center*2)/2
        
        if self.save_info_images:
            # print info on original image
            cimage=cv2.cvtColor(img_original,cv2.COLOR_GRAY2BGR)
            cv2.rectangle(cimage,(self.offset_x+487-self.width//2,self.offset_y+321-self.height//2),(self.offset_x+487+self.width//2,self.offset_y+321+self.height//2),(0,255,0),1)
            cimage = cv2.putText(cimage, "x: " + str(int(x_center_toP5-20)) + "  y: " + str(int(-y_center_toP5+20)) + "  deg: " + str((degree-min_mean+self.starting_angle)%degree), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA, False)
            cv2.circle(cimage,(int(x_center_toP5-20+487.5),int(y_center_toP5-20+321.5)),5,(0,255,0),-1)
            image = cv2.cvtColor(cimage, cv2.COLOR_BGR2GRAY)
            print(np.min(image))
            
            cv2.imwrite(save_directory + "/info_images/" + filename.split("/")[-1][:-4] + "_info_image.bmp", image)
        
        #TODO: anpassen auf allgemeinen Ursprung
        center = (round(x_center-20,2), round(-y_center+20,2))
        center_P5 = (int(x_center_toP5-20+487.5), int(y_center_toP5-20+321.5))
        rotated_deg = (degree-min_mean+self.starting_angle)%degree
        
        end = time.time()
        print("Time for one image: " + str(end-start))
        
        return center, center_P5, rotated_deg
    
    def save_results_and_stop(self, save_directory, add=None):
        with open(save_directory + "result_center_coord_P5.txt", 'w') as f:
            f.write(str(self.center_coord_P5))
        
        with open(save_directory + "result_rotated_degree.txt", 'w') as f:
            f.write(str(self.rotated_degree))
            
        if not(add==None):
            for i in add:
                datei = open(i,'r')
                text = datei.read()
                datei.close()
                begin = "\n$$$beginCenterData$$$"
                end = "$$$endCenterData$$$\n"
                if (text.find(begin) == -1) and (text.find(end) == -1):
                    text = text + begin + '\n#' + str(self.rotated_degree) + '\n#' + str(self.center_coord_P5) + end
                else:
                    cache = text[text.find(end)+len(end):]
                    text = text[:text.find(begin)]
                    text = text + begin + '\n#' + str(self.rotated_degree) + '\n#' + str(self.center_coord_P5) + end
                    text = text + cache
                with open(i, 'w') as f:
                    f.write(text)
        
        return
            