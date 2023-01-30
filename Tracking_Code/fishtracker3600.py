import cv2
import os
import time
from datetime import datetime
from datetime import timedelta
import csv

################################################## Functions #################################################

# Create a VideoCapture objects
def camera(video_camera = 0, px_width=1280,px_hight=720):
    cap = cv2.VideoCapture(video_camera)
    cap.set(3, px_width)
    cap.set(4, px_hight)
    frame_h = px_hight
    frame_w = px_width
    return cap, frame_h, frame_w

# Process camera contours:
def process_camera_contours(roi, contours, aim_rect_x, aim_rect_y, aim_rect_w, aim_rect_h, conversion_factor, time, origin_point):
   
    for cnt in contours:

            # Calculate the area and remove small elements
            area = cv2.contourArea(cnt)
            if area > 100:
                
                # Draw detection rectangles (green bounding boxes)
                x_bound, y_bound, w_bound, h_bound = cv2.boundingRect(cnt)
                cv2.rectangle(roi, (x_bound,y_bound), (x_bound + w_bound, y_bound + h_bound), (0,255,0), 2)
                
                # Calculate the center point of the bounding box
                center_x, center_y = x_bound + w_bound//2, y_bound + h_bound//2

                # Draw a circle at the center point
                cv2.circle(roi, (center_x, center_y), 3, (0, 0, 255), -1)

                # Extract the center point of the bounding box as a coordinate on the bigger rectangle
                if origin_point == 'bottom_left_corner':
                    coordinate_x, coordinate_y = center_x, aim_rect_h - (center_y - aim_rect_y)
                elif origin_point == 'bottom_right_corner':
                    coordinate_x, coordinate_y = (-center_x + aim_rect_w), aim_rect_h - (center_y - aim_rect_y)
                elif origin_point == 'top_left_corner':
                    coordinate_x, coordinate_y = (center_x, center_y)
                elif origin_point == 'top_right_corner':
                    coordinate_x, coordinate_y = (-center_x + aim_rect_w, center_y)

                # Store the coordinates
                coord_cm_time = (coordinate_x*conversion_factor,coordinate_y*conversion_factor, time)

                return coord_cm_time


# Merges two coordinate pairs and their respective timestamps, given the XY, XZ or YZ and these plane's common axis:
def coordinate_merging(plane1, plane2, common_axis='Z', tolerance=0.2, decimal_spaces=3):

    # Time threshold (seconds) used between coordinate timestamps, to be merged together
    threshold=timedelta(seconds=tolerance)

    for plane1_coordinatePairs in plane1:
        for plane2_coordinatePairs in plane2:
            
            # Between XY and XZ planes:
            if common_axis == 'X':
                if abs(plane1_coordinatePairs[0] - plane2_coordinatePairs[0])<= threshold:
                        x1, y, time1 = plane1_coordinatePairs
                        x2, z , time2 = plane2_coordinatePairs
                        x = (x1+x2)//2
                        time = (time1 + time2)//2
                        
                        # Rounds the 3D coordinate to the precision specified
                        round(x,decimal_spaces)
                        round(y,decimal_spaces)
                        round(z,decimal_spaces)
                        round(time,decimal_spaces+1)
                        xyz.append((x,y,z,time))
            
            # Between XY and YZ planes:
            elif common_axis == 'Y':
                if abs(plane1_coordinatePairs[1] - plane2_coordinatePairs[1])<= threshold:
                        x, y1, time1 = plane1_coordinatePairs
                        y2, z , time2 = plane2_coordinatePairs
                        y = (y1+y2)//2
                        time = (time1 + time2)//2

                        # Rounds the 3D coordinate to the precision specified
                        round(x,decimal_spaces)
                        round(y,decimal_spaces)
                        round(z,decimal_spaces)
                        round(time,decimal_spaces+1)
                        xyz.append((x,y,z,time))
            
            # Between XZ and YZ planes:
            elif common_axis == 'Z':
                if abs(plane1_coordinatePairs[2] - plane2_coordinatePairs[2])<= threshold:
                    x, z1, time1 = plane1_coordinatePairs
                    y, z2 , time2 = plane2_coordinatePairs
                    z= (z1+z2)//2
                    time = (time1+time2)//2

                    # Rounds the 3D coordinate to the precision specified
                    round(x,decimal_spaces)
                    round(y,decimal_spaces)
                    round(z,decimal_spaces)
                    round(time,decimal_spaces+1)
                    xyz.append((x,y,z,time))
            else:
                print('Not a suitable 3D axis')
            
            return xyz
################################################## Functions End #################################################

# Cam 1 (X,Z) & Cam 2 (Y,Z)
cap, frame_h1, frame_w1 = camera(0,1280,720)
#cap2, frame_h2, frame_w2 = camera(2,1280,720)


# Conversion factor in px to centimeters (from a fixed distance)
px_cm = 0.022570
"""Still needs to be generalized"""

# Resolution of the 20cm square in pixels on the screen.
res = 886

# Define the bigger rectangle coordinates: our aiming rectangle
big_rect_x=(frame_w1//2)-(res//2)
big_rect_z=0                        #(frame_h1//2)-(res//2)
#big_rect_y = (frame_w2//2)-(res//2)
big_rect_w = res
big_rect_h = 720
"""Still needs to be generalized"""

# Object detection from stable camera. The longer the history the more precise, but doesnt adapt to moving cameras
object_detector = cv2.createBackgroundSubtractorMOG2(history = 100, varThreshold = 50) 

# Define the file time threshold and the file size threshold
time_threshold = 300            # seconds
file_size_threshold = 100000    # bytes

# Get the current time
start_time = time.time()
now = datetime.now()

# Format the date and time as a string
date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

# Create the file name
file_name = "fish_coordinates_" + date_string + ".csv"

# Coordinate storing
xz = []                             # XZ plane corrdinates pairs
yz = []                             # YZ plane coordinates pairs
xyz = []                            # 3D merged coordinates
tolerance = 0.5  # Time threshold to compare different plane's coordinate pairs and merged them together

# Open a file in write mode
with open(file_name, "w", newline='') as csvfile:
    
    while True:

        # Read a frame from the camera
        ret, frame = cap.read()
        #ret, frame2 = cap2.read()

        height, width, _ = frame.shape
        #height2, width2,_= frame2.shape

        # Define region of interest
        roi = frame[big_rect_z:(big_rect_z+big_rect_h),big_rect_x:(big_rect_x+big_rect_w)]
        #roi2 = frame2[big_rect_z:(big_rect_z+big_rect_h),big_rect_y:(big_rect_y+big_rect_w)]

        # Moving object detection
        mask = object_detector.apply(roi)
        #mask2= object_detector.apply(roi2)

        # Clean the masks
        _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)
        #_, mask2 = cv2.threshold(mask2, 250, 255, cv2.THRESH_BINARY)

        # Find the contours of the detected object
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw the big rectangle (blue aim rectangle) on the image
        cv2.rectangle(frame, (big_rect_x, big_rect_z), (big_rect_x + big_rect_w, big_rect_z + big_rect_h), (255, 0, 0), 2)
    
        # Front Camera (X,Z)
        timestamp = time.time() - start_time
        coordinate_pair = process_camera_contours(roi, contours, big_rect_x, big_rect_z, big_rect_w, big_rect_h, px_cm, timestamp, 'bottom_left_corner')
        xz.append(coordinate_pair)     
        # Side Camera (Y,Z)
        # yz = process_camera_contours(frame2,mask2,roi2,big_rect_y,big_rect_z,big_rect_w,big_rect_h,px_cm,start_time,'bottom_right_corner',yz)
        
        # # Coordinate merging
        # xyz = coordinate_merging(xz, yz,'Z', tolerance, 3)

        # # File writing
        # writer = csv.writer(csvfile)
        # writer.writerow(['X','Y','Z','Timestamp'])
        # for row in xyz:
        #     writer.writerow(row)
        # """migth need edit: with open('merged_coordinates.csv', 'w', newline='') as csvfile:
        #                     writer = csv.writer(csvfile)
        #                     writer.writerow(['X','Y','Z','Timestamp'])
        #                     for xz_pair in xz:
        #                         for yz_pair in yz:
        #                             if abs(xz_pair[2] - yz_pair[2])<= tolerance:
        #                                 x, z1, now = xz_pair
        #                                 y, z2 , _ = yz_pair
        #                                 z= (z1+z2)//2
        #                                 xyz.append((x,y,z,now))
        #                                 writer.writerow(xyz[-1])"""

        # if os.path.getsize("fish_coordinates_"+str(date_string) + ".csv") > file_size_threshold:
        #     csvfile.close()
        #     start_time = time.time()
        #     now=datetime.now()
        #     date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        #     new_file = open("fish_coordinates_"+ str(date_string) + ".csv","w")
        #     csvfile=new_file

        # if time.time() - start_time > time_threshold:
        #     #Create new file with new name
        #     csvfile.close()
        #     start_time = time.time()
        #     now = datetime.now()
        #     date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        #     new_file = open("fish_coordinates_"+ str(date_string) + ".csv","w")
        #     csvfile = new_file

        # Display processes 
        cv2.imshow("Front RoI", roi)
        #cv2.imshow("Side RoI", roi2)

        cv2.imshow("Front view", frame)
        #cv2.imshow("Side view", frame2)
        cv2.imshow("mask 1", mask)
        #cv2.imshow("mask 2", mask2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
#cap2.release()
cv2.destroyAllWindows()