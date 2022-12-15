import cv2 

cap  = cv2.VideoCapture(0)

# object detection from stable camera
object_detector = cv2.createBackgroundSubtractorMOG2(history = 100, varThreshold = 50) 
# the longer the history more precise, but doesnt adapt to moving cameras

while True:
    ret, frame = cap.read()

    height, width, _ = frame.shape
    #print(height, width)

    # extract region of interest
    roi = frame[:140,:640] 

    # object detection
    mask = object_detector.apply(frame)
    #clean the mask
    _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
    
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:

        # calculate the area and remove small elements
        area = cv2.contourArea(cnt)
        if area > 100:
            #cv2.drawContours(roi, [cnt], -1, (0,255,0),2)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x,y), (x + w,y + h), (0,255,0), 3)

    cv2.imshow("roi", roi)
    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()