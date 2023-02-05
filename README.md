# Fish-Vision-Project: Integrated fish tracking in a small aquarium

>A project within the purview of University of Aveiro's course subject: Instrumentação Eletrónica.

Currently, the system utilizes two webcams to perform the detection of movement inside a cubic aquarium. 

The system detcts movement by using background subtraction. It then presents the detected objects in the form of green bounding boxes:

![](https://user-images.githubusercontent.com/94324481/216368908-b7704a53-c74c-46ce-b815-91f900be56f5.png)

After these bounding boxs are drawn, their center is calculated and drawn as a red point:

![](https://user-images.githubusercontent.com/94324481/216371688-529155d0-509e-46d7-8722-2d3a9017b0b9.png)

Since we want to restrict the movement detection to a single region of interest (ROI), the square face of the cubic aquarium, a blue "aim" sqaure is drwan. The movement detecion only occurs inside that area.

![](https://user-images.githubusercontent.com/94324481/216377191-1ed7b317-3fb8-43a2-8ee4-2e4a6b3e5d1d.png)

This aim was calculated in order to perform the necessary conversion between cm's and pixels on the screen. If the cameras are positioned according to this aim, the coordinates should match the real distance inside the aquarium.

The coordinates are gathered in pairs (X,Z and Y,Z), relative to the faces of the cube (and coincidentaly, our "aim" blue square). These coordinates are based on the position of the center point calculated earlier, and regarding the bottom-left and bottom-right corners as the origin points of each of these planes, respectively.

![Disposition of the systems](https://user-images.githubusercontent.com/94324481/216379256-f48aa362-622d-40e0-b459-f9a10c4b0e88.png)

The two coordinate pairs (of each square plane) are merged based on the timestamp of when they were captured. If an object is detected on one of the planes, there is a small timeframe in which that same object can be detected on the second plane, for the system to consider it the same object and merge them together.

The merging itself is done by calculating the average of the common axis between the two planes. Presently, this is the Z component between the two pairs of coordinates.

## Instructions/Future Work:

- Step 0: Assuming you are using Windows on your machine
- Step 1: Download/clone this repository
- Step 2: Run the following line of code on your cmd/terminal:

  pip install requirements.txt

- Step 3: Plug the webcams onto your PC's usb ports
- Step 4: There are 2 versions of the code (720p and 360p), choose which one you want to run and type:

  python3 720p.py

The code is still lacking some crucial aspects:

- Perform triangulation using both cameras:

  1. Calibrate the two webcams: This involves finding the intrinsic and extrinsic parameters of each camera, such as the focal length, principal point, and relative orientation and position of the cameras.

  2. Extract matching features from the two images: This involves detecting and tracking features in both images, such as corners or keypoints, that correspond to the same physical points in the scene.

  3. Compute the relative orientation and position of the cameras: This can be done using methods such as essential matrix or fundamental matrix estimation.

  4. Triangulate the 3D position of each feature: This involves using the relative orientation and position of the cameras, along with the corresponding image coordinates of each feature in both images, to compute the 3D position of each feature in the scene.

  5. Refine the 3D positions: This can be done using techniques such as bundle adjustment or robust triangulation to improve the accuracy of the 3D positions.

- Adding error handling to the code. For example, checking if the cameras are properly connected before starting to record, and handle the case if they are not.

- It would be useful to add a check to make sure that the resolution of the cameras are set correctly before starting to record.

- The current program uses a hardcoded time threshold of X seconds/byte size, it would be better to make it a user-specified parameter, or make it adjustable during the execution of the program.

- Possible addition of a GUI to the program, so that the user can interact with it more easily.

- Add a function to save the video recorded by the cameras, so that you can visualize the fish position later.

- Possibly improve the fish detection by using a more advanced object detection algorithm such as YOLO or Faster R-CNN.

- Add function to detect multiple fish in the same frame. 

## Contacts:

Leonardo Rodrigues - leonardo.r@ua.pt
