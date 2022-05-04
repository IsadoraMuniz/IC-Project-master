from tkinter import *
from PIL import Image, ImageTk

from pynput.mouse import Button, Controller # library that able the function of the mouse
import cv2 # library to de computer vision
import numpy as np # library that able to work with arrays
import wx


def videoCapture():
    cam = cv2.VideoCapture(1)
    return cam


def masksProcess(img, lowerBound, upperBound, kernelOpen, kernelClose):

    imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV) #convert BGR to HSV
    
    # create the Masks
    mask=cv2.inRange(imgHSV,lowerBound,upperBound)
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen) # removes false positive
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose) # removes false negative
    
    maskDilate = cv2.dilate(maskClose, None, iterations=0)
    # maskErode = cv2.erode(maskDilate, None, iterations=0)

    maskFinal = maskDilate

    return maskFinal


def mousePosition(camx, camy, sx, sy, mouseLoc):
    
    xf = mouseLoc[0]*sx/camx  #calculus that converts the mouse pointer to move for all the screen on axys x, also reverted
    yf = mouseLoc[1]*sy/camy # sy - mouseLoc[1]*sy/camy #calculus that converts the mouse pointer to move for all the screen on axys y
    mouse.position =(xf,yf)


def contourColor(conts, mLocOld, DampingFactor, sx, sy):

    if len(conts) > 0:
        #this block calculates the central point of the circle drawn when the color is detected  
        c = max(conts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))  

        
        if radius > 3:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
            cv2.circle(img, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(img, center, 5, (0, 0, 255), -1)

            (camx, camy) = (640, 420) #camera capture resolution
            cx = (x*sx/camx)
            cy = (y*sy/camy)
            mouseLoc = mLocOld + ((cx, cy)-mLocOld)/DampingFactor


            mousePosition(camx, camy, sx, sy, mouseLoc)




def imageShow(img):
    cv2.imshow("cam2",img)



mouse = Controller()

# lowerBound=np.array([16,57, 164])
# upperBound=np.array([41, 255, 255])

lowerBound=np.array([22,116, 129])
upperBound=np.array([179, 255, 255])

 
# lowerBound=np.array([106,159, 0])
# upperBound=np.array([179, 255, 255])


kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))

mLocOld = np.array([0,0])
mouseLoc = np.array([0,0])
DampingFactor = 2



# VIDEOCAPTURE
app = wx.App(False)
(sx, sy) = wx.GetDisplaySize() #coordinates of the size of the screen

(camx, camy) = (640, 420) #camera capture resolution
cam = videoCapture()
cam.set(3,camx)
cam.set(4, camy)


root = Tk()
root.geometry("700x540")
root.configure(bg="black")
Label(root, text="Teste cam1", font=("times new roman", 30, "bold"), bg="black", fg="red").pack()
f1 = LabelFrame(root, bg="red")
f1.pack()
L1 = Label(f1, bg="red")
L1.pack()



while(True):
    
    ret, img=cam.read() # decodes and returns the next video frame
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.flip(img, 1) # Flips a 2D array around vertical, horizontal, or both axes.
    maskFinal = masksProcess(img, lowerBound, upperBound, kernelOpen, kernelClose)

    result = cv2.bitwise_and(img, img, mask = maskFinal)

    conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    contourColor(conts, mLocOld, DampingFactor, sx, sy)

    img = ImageTk.PhotoImage(Image.fromarray(img))

    L1['image'] = img

    root.update()

    