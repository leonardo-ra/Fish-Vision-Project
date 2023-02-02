# Fish-Vision-Project: Integrated fish tracking in a small aquarium

>A project within the purview of University of Aveiro's course subject: Instrumentação Eletrónica.

Currently, the system utilizes two webcams to perform the detection of movement inside a cubic aquarium. 

The system detcts movement by using background subtraction. It then presents the detected objects in the form of green bounding boxes:

![](https://user-images.githubusercontent.com/94324481/216368908-b7704a53-c74c-46ce-b815-91f900be56f5.png)

After these bounding boxs are drawn, their center is calculated and drawn as a red point:

![](https://user-images.githubusercontent.com/94324481/216371688-529155d0-509e-46d7-8722-2d3a9017b0b9.png)

Since we want to restrict the movement detection to a single region of interest (ROI), the square face of the cubic aquarium, a blue "aim" sqaure is drwan. The movement detecion only occurs inside that area

![](https://user-images.githubusercontent.com/94324481/216377191-1ed7b317-3fb8-43a2-8ee4-2e4a6b3e5d1d.png)

This aim was calculated in order to perform the necessary conversion between cm's and pixels on the screen. If the cameras are positioned according to this aim, the coordinates should match the real distance inside the aquarium.

The coordinates are gathered in pairs (X,Z and Y,Z), relative to the faces of the cube (and coincidentaly, our "aim" blue square). These coordinates are based on the position of the center point calculated earlier, and regarding the bottom-left and bottom-right corners as the origin points of each of these planes, respectively.

![Disposition of the systems](https://user-images.githubusercontent.com/94324481/216379256-f48aa362-622d-40e0-b459-f9a10c4b0e88.png)

The two coordinate pairs (of each square plane) are merged based on the timestamp of when they were captured. If an object is detected on one of the planes, there is a small timeframe in which that same object can be detected on the second plane, for the system to consider it the same object and merge them together.

The merging itself is done by calculating the average of the common axis between the two planes. Presently, this is the Z component between the two pairs of coordinates.
