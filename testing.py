#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 15:13:59 2022

@author: testbenutzer
"""
import numpy as np

n = 11
height = 5
width = 5
num = [0,2]

        
img = np.ones((n,n))*9
img[n//2+1,n//2+1] = 5

shifted_img = np.zeros(img.shape)
shifted_img[:-height//2,:-width//2] = img[height//2+1:,width//2+1:]
print(shifted_img)
for i in range(num[0]+1,num[1]+2):
    for j in range(1, width+1):
        result_shift = np.zeros(img.shape)
        result_shift[i:,j:] = shifted_img[:-i,:-j]
        print(result_shift)

a = [1,2,3,4,5,6,7,8,9,10]
print(a[-0])
        
"""
shifted_img = np.zeros(self.img.shape)
shifted_img[:-self.height//2,:-self.width//2] = self.img[self.height//2+1:,self.width//2+1:]
for i in range(self.num[0]+1, self.num[1]+2):
    for j in range(1,self.width+1):
        result_shift = np.zeros(self.img.shape)
        result_shift[i:,j:] = shifted_img[:-i,:-j]
"""