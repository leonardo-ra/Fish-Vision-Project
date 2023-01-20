import cv2 

cap  = cv2.VideoCapture(1)

cap.set(3, 1280)
cap.set(4, 720)
h_aim = 720
w_aim = 1280
res=548
x_aim0=int((w_aim/2-res/2))
y_aim0=int((h_aim/2-res/2))
x_aim1=int((w_aim/2+res/2))
y_aim1=int((h_aim/2+res/2))
px_cm=0.036458333
origin = (y_aim1,x_aim0)
    
# object detection from stable camera
object_detector = cv2.createBackgroundSubtractorMOG2(history = 100, varThreshold = 50) 
# the longer the history more precise, but doesnt adapt to moving cameras

while True:
    ret, frame = cap.read()

    height, width, _ = frame.shape
    #print(height, width)

    # extract region of interest
    #roi = cv2.rectangle(frame,(x_aim0,y_aim0),(x_aim1,y_aim1),(255,0,0),2)
    roi = frame[y_aim0:y_aim1,x_aim0:x_aim1]

    # object detection
    mask = object_detector.apply(roi)
    #clean the mask
    _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.rectangle(frame,(x_aim0,y_aim0),(x_aim1,y_aim1),(255,0,0),1) #aim square (blue)
    
    for cnt in contours:

        # calculate the area and remove small elements
        area = cv2.contourArea(cnt)
        if area > 100:
            cv2.drawContours(roi, [cnt], -1, (255,0,0),2)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(roi, (x,y), (x + w,y + h), (0,255,0), 3) #green square
            x2 = x + int(w/2) #calculate center X
            y2 = y + int(h/2) #calculate center Y
            center_point = (y2,x2) #center point of the rectangle is given in Y,X order
            print("centro em pixeis = " + str(center_point) +'\n')
            print("origem em pixeis = " + str(origin) + "\n")
            cv2.circle(roi,center_point,4,(0,0,255),-2) #draws center point 
            position_px= ((center_point[0]-origin[0]),(center_point[1]-origin[1])) #center point - origin = distance from origin in pixels
            position_cm = (position_px[0]*px_cm,position_px[1]*px_cm) #distance from origin in cm
            coord="x(cm): " + str(position_cm[0]) + ", y(cm)" + str(position_cm[1])
            print("position em cm = " + str(position_cm) + "\n")
            print("coord = " + coord)
            #coord_disp = float("{:.2f}".format{coord}) 
            cv2.putText(frame,coord,(x2,y2+20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)






    cv2.imshow("roi", roi)
    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()