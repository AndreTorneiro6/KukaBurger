import cv2
import numpy as np

# RGB values for orange color
lower_orange = np.array([0, 52, 0], dtype=np.uint8)
upper_orange = np.array([11, 168, 215], dtype=np.uint8)


# Function to find top left and top right corners in orange area
def find_corners(image):
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Filter the image to get only the orange color
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Dilate and erode the mask to remove noise
    kernel = np.ones((13, 13), np.uint8)
    img_dilation = cv2.dilate(mask, kernel, iterations=1)
    kernel = np.ones((13, 13), np.uint8)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

    # Find contours in the eroded image
    contours, _ = cv2.findContours(img_erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Blank image for drawing contours (optional)
    blank = np.zeros(img_erosion.shape[:2], dtype='uint8')

    # Find top left and top right corners in the orange area
    for contour in contours:
        if cv2.contourArea(contour) > 200:
            # Find bounding rectangle around the contour
            _, _, w, _ = cv2.boundingRect(contour)

    return w


# Function to find distance
def find_distance(frame):
    # Split the frame to focus on a specific area
    height, width, _ = frame.shape
    meio_y = height // 3
    meio_x = width // 4
    frame_split = frame[80:meio_y, :meio_x, :]

    # Find top left and top right corners in the orange area
    top_left_point = find_corners(frame_split)

    # Return the calculated distance
    return top_left_point * 1.28

# Code below is commented out, presumably for testing or integration purposes
