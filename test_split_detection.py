#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 11:45:12 2021

@author: testbenutzer
"""

import numpy as np
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
from scipy.ndimage.measurements import label
import matplotlib.pyplot as pp
import cv2
import Basicfunctions_GUI as bsf
import os
from time import gmtime, strftime

def detect_peaks(image):
    """
    Takes an image and detect the peaks using the local maximum filter.
    Returns a boolean mask of the peaks (i.e. 1 when
    the pixel's value is the neighborhood maximum, 0 otherwise)
    """

    # define an 8-connected neighborhood
    neighborhood = generate_binary_structure(2,2)

    #apply the local maximum filter; all pixel of maximal value 
    #in their neighborhood are set to 1
    local_max = maximum_filter(image, footprint=neighborhood)==image
    #local_max is a mask that contains the peaks we are 
    #looking for, but also the background.
    #In order to isolate the peaks we must remove the background from the mask.

    #we create the mask of the background
    background = (image==0)

    #a little technicality: we must erode the background in order to 
    #successfully subtract it form local_max, otherwise a line will 
    #appear along the background border (artifact of the local maximum filter)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    #we obtain the final mask, containing only peaks, 
    #by removing the background from the local_max mask (xor operation)
    detected_peaks = local_max ^ eroded_background
    
    return detected_peaks


def split_detection(image, delta=40, increment=40, min_area=50, max_area=250, min_percent_nonblack=50):
    original = np.copy(image)
    mean = np.zeros((1286,))
    for i in range(mean.shape[0]//2):
        mean[i] = np.mean(image[i][delta:488-delta])
        mean[643+i] = np.mean(image[i][488+delta:975-delta])
    
    image[image < int(np.max(mean)+increment)] = np.max(mean)+increment
    image = (image-np.min(image))*255.0/(np.max(image)-np.min(image))
    image = image.astype('uint8')
    
    mD, sD, _ = bsf.maxFinder_large(image, None)
    image_dots_new = np.copy(image)
    image_dots_new = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    
    dots = mD + sD
    dot_num = []
    dot_mean = []
    
    end = False
    
    if len(dots) < 1:
        return original, 0
    
    for dot in dots:    
        area = cv2.contourArea(dot)
        
        if  area < max_area and area > min_area:
            x,y,w,h = cv2.boundingRect(dot)
            ausschnitt = image[y:y+h,x:x+w]
            
            mean = int(int(bsf.dotMean(image,dot)) * 255/np.max(ausschnitt))
            dot_mean.append(mean)
            #if mean > 30:
            detected_peaks = detect_peaks(ausschnitt)
            ausschnitt_peaks = detected_peaks*ausschnitt
            
            _, num_features = label(ausschnitt_peaks)
            
            #if num_features < 10:
            percent_nonblack = int(100 * np.count_nonzero(ausschnitt)/(ausschnitt.shape[0]*ausschnitt.shape[1]))
            if percent_nonblack > min_percent_nonblack:
                dot_num.append(num_features)
                
                cv2.rectangle(image_dots_new,(x,y),(x+w,y+h),(0,255,0),1)
                image_dots_new = cv2.putText(image_dots_new, str(num_features), (x+w,y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,100), 1, cv2.LINE_AA, False)
                image_dots_new = cv2.putText(image_dots_new, str(int(percent_nonblack)), (x+w,y+h+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,100), 1, cv2.LINE_AA, False)
                end = True
     
    average_dots = np.mean(dot_num)
    print("average dots per contur: " + str(round(average_dots,1)))
    average_mean = np.mean(dot_mean)
    print("average mean per contur: " + str(round(average_mean,1)))
    
    if end:
        return image_dots_new, average_dots
    else:
        return original, average_dots


filelist = ["test_split_detection_image.bmp", "test_split_detection_image.bmp", "Recht_20kV30mA_40p0mm_1800s_ohne_poly_000.bmp", "ACK_101_20kV30mA_40p0mm_3600s_test_nebenmaxima_verschwommen_000.bmp", "test_split_detection_image_2.bmp"]
i = 0

open_directory = "/home/testbenutzer/Schreibtisch/Laue-Software/GUI/JUK/4PunkteVerzwilligung/Proben ACK/101/ACK_101_20kV30mA_40p0mm_RASTER_840s_20x24_0.25mm_continuous_nach_bugfix/Raster_Bg_Removed"
save_directory = "/home/testbenutzer/Schreibtisch/Laue-Software/GUI/JUK/4PunkteVerzwilligung/Proben ACK/101/ACK_101_20kV30mA_40p0mm_RASTER_840s_20x24_0.25mm_continuous_nach_bugfix/Raster_Bg_Removed_split_detection/"
result = [f for f in os.listdir(open_directory) if os.path.isfile(os.path.join(open_directory, f))]
filenames = []
for j in sorted(result):
    filenames.append(str(open_directory) + "/" + str(j))
    
datei = open(filenames[len(filenames)-1],'r')
text = datei.read().split('#',2)
datei.close()
logfile = text[0]
text_arr = text[1]
        
filenames = filenames[:-1]
where_split = np.zeros((24,20))

for file in filenames:
    print(i)
    position = (i//where_split.shape[1], i%where_split.shape[1])
    print(file)
    image = cv2.imread(file, -1)
    image_dots_new, average_dots = split_detection(image)
    
    if len(image_dots_new.shape) > 2:
        grayImage = cv2.cvtColor(image_dots_new, cv2.COLOR_BGR2GRAY)
    else:
        grayImage = np.copy(image_dots_new)
    
    new_save_directory = save_directory + strftime("%Y%m%d%H%M%S", gmtime()) + "_" + "(" + str(position[0]) + "," + str(position[1]) + ").tif"
    cv2.imwrite(new_save_directory, grayImage)

    if average_dots >  2:
        where_split[position] = 2
    elif average_dots > 0:
        where_split[position] = 1
    i = i + 1

text_arr = str(where_split)
with open(save_directory + strftime("%Y%m%d%H%M%S", gmtime()) + "_" + "_logfile.txt", 'w') as f:
    f.write(logfile + "#" + text_arr)
pp.imshow(where_split)
"""

path = "test_mittelpunkt_detection.tif"

original_arr = cv2.imread(path, -1)
original_arr = np.uint8(original_arr)
mD, sD, dot_image = bsf.maxFinder_large(original_arr, None)
coord_mD = []

for dot in mD:
    x,y,w,h = cv2.boundingRect(dot)
    coord_mD.append((round(x+w/2,2),round(y+h/2,2)))
    
print(coord_mD)
    
"""



















































