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
(R1, R2, P1, P2, Q, roi1, roi2) = cv2.stereoRectify(cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, (right_image.shape[0], right_image.shape[1]), R, T, R1, R2, P1, P2, Q=Q, flags=cv2.CALIB_ZERO_DISPARITY, alpha=-1, newImageSize=(0,0))

right_maps = cv2.initUndistortRectifyMap(cameraMatrix1, distCoeffs1, R1, P1, (right_image.shape[0], right_image.shape[1]), cv2.CV_16SC2)
left_maps = cv2.initUndistortRectifyMap(cameraMatrix2, distCoeffs2, R2, P2, (right_image.shape[0], right_image.shape[1]), cv2.CV_16SC2)

np.savetxt('right_maps.txt', right_maps)

print right_maps

print right_maps[0]

"""
np.savetxt('R1_mat.txt',R1)
np.savetxt('R2_mat.txt',R2)
np.savetxt('P1_mat.txt',P1)
np.savetxt('P2_mat.txt',P2)
"""
np.savetxt('Q_mat.txt',Q)
