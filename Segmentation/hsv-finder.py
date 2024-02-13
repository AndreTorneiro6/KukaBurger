import cv2
import numpy as np

# Trackbar callback function to update HSV value
def callback(x):
    global H_low, H_high, S_low, S_high, V_low, V_high
    # Assign trackbar position value to H, S, V High and Low variables
    H_low = cv2.getTrackbarPos('low H', 'controls')
    H_high = cv2.getTrackbarPos('high H', 'controls')
    S_low = cv2.getTrackbarPos('low S', 'controls')
    S_high = cv2.getTrackbarPos('high S', 'controls')
    V_low = cv2.getTrackbarPos('low V', 'controls')
    V_high = cv2.getTrackbarPos('high V', 'controls')

# Create a window for trackbars
cv2.namedWindow('controls', 2)
# Resize the window
cv2.resizeWindow("controls", 550, 10)

# Initialize global variables for HSV ranges
H_low = 0
H_high = 179
S_low = 0
S_high = 255
V_low = 0
V_high = 255

# Create trackbars for low and high values of H, S, V
cv2.createTrackbar('low H', 'controls', 0, 179, callback)
cv2.createTrackbar('high H', 'controls', 179, 179, callback)
cv2.createTrackbar('low S', 'controls', 0, 255, callback)
cv2.createTrackbar('high S', 'controls', 255, 255, callback)
cv2.createTrackbar('low V', 'controls', 0, 255, callback)
cv2.createTrackbar('high V', 'controls', 255, 255, callback)

# Open the camera
cam = cv2.VideoCapture(0)
while (1):
    # Read source image
    img = cv2.imread('./images/ingredients.png')

    # Convert source image to HSV color mode
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define HSV range based on trackbar values
    hsv_low = np.array([H_low, S_low, V_low], np.uint8)
    hsv_high = np.array([H_high, S_high, V_high], np.uint8)

    # Create mask for HSV range
    mask = cv2.inRange(hsv, hsv_low, hsv_high)
    # Apply mask to the original image
    res = cv2.bitwise_and(img, img, mask=mask)

    # Show segmented image
    cv2.imshow('segmentation', res)

    # Wait for the user to press escape and break the loop
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

# Close all windows
cv2.destroyAllWindows()
