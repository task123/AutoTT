import numpy as np
import cv2
import time
#from matplotlib import pyplot as plt

'''
camera = cv2.VideoCapture(0)
time.sleep(0.5)
_,imgL = camera.read()
print "move camera"
time.sleep(1)
_,imgR = camera.read()
'''
imgR = cv2.imread('right2.jpeg')
imgL = cv2.imread('left2.jpeg')

stereo = cv2.StereoSGBM_create(minDisparity =0,numDisparities=160, blockSize=12,speckleWindowSize = 5,speckleRange=5,uniquenessRatio=3)
#stereo = cv2.StereoSGBM_create(minDisparity =1,numDisparities=320, blockSize=3, P1 = 1, P2 = 2,uniquenessRatio=1,speckleWindowSize = 13)
#stereo = cv2.StereoSGBM_create(minDisparity =1,numDisparities=320, blockSize=10)
disparity = stereo.compute(imgL,imgR)#plt.imshow(disparity,'gray')
#plt.show()
#cv2.imshow('test',disparity)
#print disparity

maksList = []
for i in range(0,len(disparity)):
    maksList.append(max(disparity[i]))
maks = max(maksList).astype(np.float32)
#print maks.astype(np.float32)
disparity2 = disparity/maks
#print disparity2

disparity2=cv2.GaussianBlur(disparity2,(9,9),0)
threshold = cv2.inRange(disparity2,np.array((0.999), dtype = "uint8"),np.array((255), dtype = "uint8"))
thesh_image = cv2.bitwise_and(disparity2, disparity2, mask=threshold )

height,width = thesh_image.shape
print thesh_image.shape
distance_ROI = thesh_image[int(3.0*height/4.0):int(height),int(width/4.0):int(3.0*width/4.0)]

print int(3.0*height/4.0)
print int(height)
print int(width/4.0)
print int(3.0*width/4.0)

rows,cols = distance_ROI.shape
print distance_ROI.shape
distance_avg=0
for row in range(0,rows):
    for col in range(0,cols):
        distance_avg = distance_avg + distance_ROI[row,col]
distance_avg = distance_avg/distance_ROI.size
print distance_avg




cv2.imshow('disp',disparity2)
cv2.imshow('tres',distance_ROI)



cv2.waitKey(30000)