import cv2
import os
import time
from datetime import datetime

# Create a VideoCapture object
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
h_aim = 720
w_aim = 1280

# Conversion factor in px to centimeters
px_cm=0.036458333

# Resolution of the 20cm^3 square in pixels. Determined by measuring physical distance between camera and object
res=548

# Define the bigger rectangle coordinates, our aiming rectangle
big_rect_x=(w_aim//2)-(res//2)
big_rect_z=(h_aim//2)-(res//2)
big_rect_w = res
big_rect_h = res 

# object detection from stable camera. The longer the history the more precise, but doesnt adapt to moving cameras
object_detector = cv2.createBackgroundSubtractorMOG2(history = 100, varThreshold = 50) 

# Define the time threshold and the file size threshold
time_threshold = 300 # seconds
file_size_threshold = 100 # bytes

# Get the current time
start_time = time.time()

now = datetime.now()

# Format the date and time as a string
date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

# Create the file name
file_name = "fish_coordinates_" + date_string + ".txt"

# Open a file in write mode
with open(file_name, "w") as file:

    while True:

        # Read a frame from the camera
        ret, frame = cap.read()
        height, width, _ = frame.shape

        # Define region of interest
        roi = frame[big_rect_z:(big_rect_z+big_rect_h),big_rect_x:(big_rect_x+big_rect_w)]
        
        # Moving object detection
        mask = object_detector.apply(roi)
        
        # Clean the mask
        _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)

        # Find the contours of the detected object
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw the big rectangle (blue aim rectangle) on the image
        cv2.rectangle(frame, (big_rect_x, big_rect_z), (big_rect_x + big_rect_w, big_rect_z + big_rect_h), (255, 0, 0), 2)
        
        
        for cnt in contours:

            # Calculate the area and remove small elements
            area = cv2.contourArea(cnt)
            if area > 100:
                
                # Draw detection rectangles (green bounding boxes)
                x_bound, z_bound, w_bound, h_bound = cv2.boundingRect(cnt)
                cv2.rectangle(roi, (x_bound,z_bound), (x_bound + w_bound,z_bound + h_bound), (0,255,0), 2)

                # Draw blue contours around the detected object
                #cv2.drawContours(roi, [cnt], -1, (255,0,0),2)
                
                # Calculate the center point of the bounding box
                center_x, center_z = x_bound + w_bound//2, z_bound + h_bound//2

                # Draw a circle at the center point
                cv2.circle(roi, (center_x, center_z), 3, (0, 0, 255), -1)
                
                # Extract the center point of the bounding box as a coordinate on the bigger rectangle
                coordinate_x, coordinate_z = center_x, big_rect_h - (center_z - big_rect_z)
                # para o canto inferior direito (segunda câmara) é fazer: coordinate_x, coordinate_y = center_x - (big_rect_x+big_rect_w), big_rect_h - (center_y - big_rect_y)
                coord_px = (coordinate_x,coordinate_z)
                coord_cm = (coordinate_x*px_cm,coordinate_z*px_cm)

                # Formating
                formatted_coord_cm = tuple(round(num,2) for num in coord_cm)

                # Print the coordinates on the terminal
                print(f"Coordinates in cm's (X,Z) = ({formatted_coord_cm[0]:.2f}, {formatted_coord_cm[1]:.2f})",end='',flush=True)
                print('\r')

                # Print the coordinates on captured frame 
                coord_text = f"(x,z): {formatted_coord_cm[0]:.2f},{formatted_coord_cm[1]:.2f}"
                cv2.putText(roi,coord_text,(coord_px[0],coord_px[1]),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)        
                """ still buggy... """

                # Write the coordinates to the file
                file.write(str(round(coord_cm[0],4)) + ',' + str(round(coord_cm[1],3)) + "\n")
                    
                if os.path.getsize("fish_coordinates_"+str(date_string) + ".txt") > file_size_threshold:
                    file.close()
                    start_time=time.time()
                    now=datetime.now()
                    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
                    new_file = open("fish_coordinates_"+ str(date_string) + ".txt","w")
                    file=new_file

        if time.time() - start_time > time_threshold:
            #Create new file with new name
            file.close()
            start_time=time.time()
            now = datetime.now()
            date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
            new_file = open("fish_coordinates_"+ str(date_string) + ".txt","w")
            file=new_file


        # Display processes 
        cv2.imshow("roi", roi)
        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()