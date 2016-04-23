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
     right_image = cv2.imread("chess_images/chessboard_right_" + str(i) + ".png")
     left_image = cv2.imread("chess_images/chessboard_left_" + str(i) + ".png")
     right_gray = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)
     left_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
     ret, right_corners = cv2.findChessboardCorners(right_gray, (num_of_vertical_crosses_on_chessboard, num_of_horizontal_crosses_on_chessboard))
     rightImagePoints.append(right_corners)
     ret, left_corners = cv2.findChessboardCorners(left_gray, (num_of_vertical_crosses_on_chessboard, num_of_horizontal_crosses_on_chessboard))
     leftImagePoints.append(left_corners)
     corner_points = []
     for h in range(0, num_of_horizontal_crosses_on_chessboard):
          for v in range(0, num_of_vertical_crosses_on_chessboard):
               corner_points.append((v*width_of_squares, h*width_of_squares, 0))
     objectPoints.append(corner_points)
     
     print objectPoints
     print rightImagePoints
     print leftImagePoints
     print right_image.shape[:2]
     cameraMatrix1 = []
     distCoeffs1= []
     cameraMatrix2= []
     distCoeffs2=[]
     retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(objectPoints, rightImagePoints, leftImagePoints, cameraMatrix1,distCoeffs1, cameraMatrix2, distCoeffs2, right_image.shape[:2], )
     R1 = []
     R2 = []
     P1 = []
     P2 = []
     Q = []
     (roi1, roi2) = cv2.StereoRectify(cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2,(right_image.height, right_image.widht), R, T, R1, R2, P1, P2, Q, CALIB_ZERO_DISPARITY, -1, (0, 0))
     print "roi1" 
     print roi1
     print "roi2"
     print roi2
     print  Q
     np.savetxt('Q_mat.txt',Q)
