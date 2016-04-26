#!/usr/bin/env python

import cv2
import numpy as np
import time

cameraMatrix1 = np.loadtxt('calibrationMatrices/cameraMatrix1_mat.txt')
cameraMatrix2 = np.loadtxt('calibrationMatrices/cameraMatrix2_mat.txt')
distCoeffs1 = np.loadtxt('calibrationMatrices/distCoeffs1_mat.txt')
distCoeffs2 = np.loadtxt('calibrationMatrices/distCoeffs2_mat.txt')
R1 = np.loadtxt('calibrationMatrices/R1_mat.txt')
R2 = np.loadtxt('calibrationMatrices/R2_mat.txt')
P1 = np.loadtxt('calibrationMatrices/P1_mat.txt')
P2 = np.loadtxt('calibrationMatrices/P2_mat.txt')


#enter = raw_input("To take left picture, press enter.")
imgL = cv2.imread('left.jpeg')
#enter = raw_input("To take right picture 2, press enter")
imgR = cv2.imread('right.jpeg')

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
#stereo = cv2.StereoSGBM_create(numDisparities = 96, blockSize = 25 ) #blockSize must be odd
stereo = cv2.StereoSGBM_create(minDisparity = 0, numDisparities = 16, blockSize = 5 )

print('computing disparity...')
imgL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
imgR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)
disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0
print disp
np.savetxt('disp.txt',disp)

points = cv2.reprojectImageTo3D(disp, Q)
print points
colors = imgL
mask = disp > disp.min()
out_points = points[mask]
out_colors = colors[mask]

#cv2.imshow('left', imgL)
cv2.imwrite('disparity.jpeg', (disp-min_disp)/num_disp)
