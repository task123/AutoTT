import cv2
import numpy as np
import time

num_of_pictures = raw_input("how many picures pairs are there?")
num_of_horizontal_crosses_on_chessboard = 7
num_of_vertical_crosses_on_chessboard = 7
width_of_squares = 2.5

objectPoints = []
rightImagePoints = []
leftImagePoints = []

for i in [1,2,3,4,5,6,11]:
    #print i
    right_image = cv2.imread("chess_images/chessboard_right_" + str(i) + ".png")
    left_image = cv2.imread("chess_images/chessboard_left_" + str(i) + ".png")
    right_gray = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)
    left_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
    ret, right_corners = cv2.findChessboardCorners(right_gray, (num_of_vertical_crosses_on_chessboard, num_of_horizontal_crosses_on_chessboard))
    #print right_corners
    rightImagePoints.append(right_corners)
    ret, left_corners = cv2.findChessboardCorners(left_gray, (num_of_vertical_crosses_on_chessboard, num_of_horizontal_crosses_on_chessboard))
    leftImagePoints.append(left_corners)
    corner_points = []
    for h in range(0, num_of_horizontal_crosses_on_chessboard):
      for v in range(0, num_of_vertical_crosses_on_chessboard):
           tempArray = [v*width_of_squares, h*width_of_squares, 0]
           tempArray = np.float32(tempArray)
           corner_points.append(tempArray)
    objectPoints.append(corner_points)

objectPoints = np.asarray(objectPoints)

cameraMatrix1 = np.empty(right_image.shape[:2])
distCoeffs1= np.empty((4,4))
cameraMatrix2= np.empty(right_image.shape[:2])
distCoeffs2= np.empty((4,4))
retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(objectPoints, rightImagePoints, leftImagePoints, cameraMatrix1,distCoeffs1, cameraMatrix2, distCoeffs2, right_image.shape[:2], flags=cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_ZERO_TANGENT_DIST)
R1 = np.empty((3,3))
R2 = np.empty((3,3))
P1 = np.empty((3,4))
P2 = np.empty((3,4))
Q = np.empty((4,4))
print right_image.shape[0]
(roi1, roi2, test1, test2,test3,test4,test5) = cv2.stereoRectify(cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, (right_image.shape[0], right_image.shape[1]), R, T, R1, R2, P1, P2, Q=Q, flags=cv2.CALIB_ZERO_DISPARITY, alpha=-1, newImageSize=(0,0))
print "roi1" 
print roi1
print "roi2"
print roi2
print"test 1"
print test1
print"test 2"
print test2
print"test 3"
print test3
print"test 4"
print test4
print"test 5"
print test5
np.savetxt('Q_mat.txt',Q)
