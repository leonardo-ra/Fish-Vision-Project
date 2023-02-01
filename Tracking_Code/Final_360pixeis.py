import cv2
import os
import time
from datetime import datetime
from datetime import timedelta
import csv

# Create a VideoCapture object

# Cam 1 (X,Z)
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 360)
h_aim = 360
w_aim = 640

# Cam 2 (Y,Z)
cap2 = cv2.VideoCapture(1)
cap2.set(3, 640)
cap2.set(4, 360)

# Conversion factor in px to centimeters
px_cm=0.08972222

# Resolution of the 20cm^3 square in pixels. Determined by measuring physical distance between camera and object
res=222

# Define the bigger rectangle coordinates, our aiming rectangle
big_rect_x=(w_aim//2)-(res//2)
big_rect_z=(h_aim//2)-(res//2) 
big_rect_y=(w_aim//2)-(res//2)
big_rect_w = res
big_rect_h = res

# object detection from stable camera. The longer the history the more precise, but doesnt adapt to moving cameras
object_detector = cv2.createBackgroundSubtractorMOG2(history = 100, varThreshold = 50) 
object_detector2 = cv2.createBackgroundSubtractorMOG2(history= 100, varThreshold = 50) 

# Define the time threshold and the file size threshold
time_threshold = 600 # seconds
file_size_threshold = 1000000 # bytes

# Get the current time
start_time = time.time()

now = datetime.now()

# Format the date and time as a string
date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

# Create the file name
file_name = "fish_coordinates_" + date_string + ".csv"

# Coordinate storing
xz = []
yz = []
xyz = []
tolerance = 0.5

# Open a file in write mode
with open(file_name, "w",newline='') as csvfile:
    
    while True:

        # Read a frame from the cameras
        ret, frame = cap.read()
        ret2,frame2 = cap2.read()

        height, width, _ = frame.shape
        height2,width2, _ = frame2.shape

        # Define region of interest
        roi = frame[big_rect_z:(big_rect_z+big_rect_h),big_rect_x:(big_rect_x+big_rect_w)]
        roi2 = frame2[big_rect_z:(big_rect_z+big_rect_h),big_rect_y:(big_rect_y+big_rect_w)]

        # Moving object detection
        mask = object_detector.apply(roi)
        mask2= object_detector2.apply(roi2)

        # Clean the masks
        _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
        _, mask2 = cv2.threshold(mask2, 250, 255, cv2.THRESH_BINARY)

        # Find the contours of the detected object
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(mask2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # Draw the big rectangle (blue aim rectangle) on the image
        cv2.rectangle(frame, (big_rect_x, big_rect_z), (big_rect_x + big_rect_w, big_rect_z + big_rect_h), (255, 0, 0), 2)
        cv2.rectangle(frame2,(big_rect_y, big_rect_z), (big_rect_y + big_rect_w, big_rect_z + big_rect_h), (255, 0, 0), 2)
        
        # Front Camera (X,Z)
        for cnt in contours:

            # Calculate the area and remove small elements
            area = cv2.contourArea(cnt)
            if area > 100:
                
                # Draw detection rectangles (green bounding boxes)
                x_bound, z_bound, w_bound, h_bound = cv2.boundingRect(cnt)
                cv2.rectangle(roi, (x_bound,z_bound), (x_bound + w_bound, z_bound + h_bound), (0,255,0), 2)
                
                # Calculate the center point of the bounding box
                center_x, center_z = x_bound + w_bound//2, z_bound + h_bound//2

                # Draw a circle at the center point
                cv2.circle(roi, (center_x, center_z), 3, (0, 0, 255), -1)

                # Extract the center point of the bounding box as a coordinate on the bigger rectangle
                coordinate_x, coordinate_z = center_x, big_rect_h - (center_z - big_rect_z)
                coord_px = (coordinate_x,coordinate_z)
                timestamp=time.time()-start_time
                coord_cm = (coordinate_x*px_cm,coordinate_z*px_cm, timestamp)

                # Store the coordinates
                xz.append(coord_cm)

        #Side Camera (Y,Z)
        for cnt in contours2:    
            # Calculate the area and remove small elements
            area = cv2.contourArea(cnt)
            if area > 100:
                
                # Draw detection rectangles (green bounding boxes)
                y_bound, z_bound2, w_bound2, h_bound2 = cv2.boundingRect(cnt)
                cv2.rectangle(roi2, (y_bound,z_bound2), (y_bound + w_bound2, z_bound2 + h_bound2), (0,255,0), 2)

                # Calculate the center point of the bounding box
                center_y,center_z = y_bound + w_bound2//2, z_bound2 + h_bound2//2

                # Draw a circle at the center point
                cv2.circle(roi2, (center_y, center_z),3, (0, 0, 255), -1)

                # Extract the center point of the bounding box as a coordinate on the bigger rectangle
                coordinate_y,coordinate_z = (-center_y + big_rect_w), big_rect_h - (center_z - big_rect_z) 
                coord_px2 = (coordinate_y,coordinate_z)
                timestamp=time.time()-start_time
                coord_cm2 = (coordinate_y*px_cm,coordinate_z*px_cm, timestamp)

                # Store the coordinates
                yz.append(coord_cm2)
                
        # Display processes 
        cv2.imshow("Front RoI", roi)
        cv2.imshow("Side RoI",roi2)

        cv2.imshow("Front view", frame)
        cv2.imshow("Side view",frame2)

        #cv2.imshow("mask 1", mask)
        #cv2.imshow("mask 2",mask2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    writer = csv.writer(csvfile)
    #writer.writerow(['X','Y','Z','Timestamp'])
    for xz_pair in xz:
        for yz_pair in yz:
            if abs(xz_pair[2] - yz_pair[2]) <= tolerance:
                x, z1, time1 = xz_pair
                y, z2 , time2 = yz_pair
                z= (z1+z2)/2
                x = round(x,3)
                y = round(y,3)
                z = round(z,3)
                time1 = round(time1,3)
                xyz.append((x,y,z,time1))
                for row in xyz:
                    writer.writerow(row)

                    if os.path.getsize("fish_coordinates_"+str(date_string) + ".csv") > file_size_threshold:
                        csvfile.close()
                        start_time = time.time()
                        now=datetime.now()
                        date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
                        new_file = open("fish_coordinates_"+ str(date_string) + ".csv","w")
                        csvfile=new_file

                    if time.time() - start_time > time_threshold:
                        #Create new file with new name
                        csvfile.close()
                        start_time = time.time()
                        now = datetime.now()
                        date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
                        new_file = open("fish_coordinates_"+ str(date_string) + ".csv","w")
                        csvfile = new_file


cap.release()
cap2.release()
cv2.destroyAllWindows()