#!/usr/bin/env python

import cv2
import numpy as np

Q = np.loadtxt('Q_mat.txt')



cap = cv2.VideoCapture(0)

enter = raw_input("To take left picture, press enter.")
_, imgL = cap.read()
imgL = cv2.resize(imgL,(640,480))
enter = raw_input("To take right picture 2, press enter")
_, imgR = cap.read()
imgR = cv2.resize(imgR,(640,480))

#window_size = 3
min_disp = 16
num_disp = 112-min_disp
"""
    stereo = cv2.StereoSGBM_create(minDisparity = min_disp,
    numDisparities = num_disp,
    blockSize = 16,
    P1 = 8*3*window_size**2,
    P2 = 32*3*window_size**2,
    disp12MaxDiff = 1,
    uniquenessRatio = 10,
    speckleWindowSize = 100,
    speckleRange = 32
    )
    """
#stereo = cv2.StereoBM(cv2.STEREO_BM_BASIC_PRESET,ndisparities=96, SADWindowSize=25)
stereo = cv2.createStereoBM(numDisparities = 96, blockSize = 25 ) #blockSize must be odd

print('computing disparity...')
imgL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
imgR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)
disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

points = cv2.reprojectImageTo3D(disp, Q)
colors = imgL
mask = disp > disp.min()
out_points = points[mask]
out_colors = colors[mask]
    
cv2.imshow('left', imgL)
cv2.imshow('disparity', (disp-min_disp)/num_disp)

