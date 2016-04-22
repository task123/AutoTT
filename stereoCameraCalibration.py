import cv2
import numpy as np


objpts=[] 
objPoints = []
pointCounts = hor*ver 
R = [8]
T = [8]
E=[]
F=[]
R1 = [] 
R2 = [] 
P1=[] 
P2 =[]
objectPoints = [] 
imgPoints1 = [] 
imgPoints2 = [] 
imagePoints2 = [] 
imagePoints1 = []

webCamHndlr_r = cv2.VideoCapture(0)
webCamHndlr_l = cv2.VideoCapture(1)

while ((len(imagePoints1) < hor*ver) and (len(imagePoints2)< hor*ver)):

     ret,imgr  = webCamHndlr_r.read(0)
     ret,imgl  = webCamHndlr_l.read(1)
     grey_imgr = cv2.cvtColor(imgr, cv.CV_BGR2GRAY)
     grey_imgl = cv2.cvtColor(imgl, cv.CV_BGR2GRAY)
     ret, cornersr =cv2.findChessboardCorners(grey_imgr,dims)
     cv2.drawChessboardCorners(grey_imgr,dims,cornersr,0)
     ret, cornersl =cv2.findChessboardCorners(grey_imgl,dims)
     cv2.drawChessboardCorners(grey_imgl,dims,cornersl,0)
     cv2.imshow("chessboard", grey_imgr)
     cv2.imshow("chessboard1", grey_imgl)

     objPoints = np.zeros((hor*ver,3), np.float32)
     objPoints[:,:2] = np.mgrid[0:hor,0:ver].T.reshape(-1,2)

     if cv.WaitKey(-1) == 32:

          imagePoints1.append(cornersl)
          imagePoints2.append(cornersr)
          print len(imagePoints1)
          objectPoints.append(objPoints)
          cv2.imwrite("./test_images/img_r"+str(i)+".jpg",imgr)
          cv2.imwrite("./test_images/img_l"+str(i)+".jpg",imgl)
          i = i+1;


          if cv2.waitKey(10) == 27:
               break
objectPoints = [np.asarray(x) for x in objectPoints]
imagePoints1 = [np.asarray(x) for x in imagePoints1]
imagePoints2 = [np.asarray(x) for x in imagePoints2]

if( len(imagePoints1[0])== len(imagePoints2[0]) == len(objectPoints[0]) == len(objectPoints)== len(imagePoints2) == len(imagePoints1) ) : print len(imagePoints1[0])

       retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(objectPoints, imagePoints1, imagePoints2, (320,240))
       print R

       cv.StereoRectify(cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2,(imgr.width,imgr.height), R, T, R1, R2, P1, P2, Q, CV_CALIB_ZERO_DISPARITY, -1, (0, 0))
       print  Q
       np.savetxt('Q_mat.txt',Q)
