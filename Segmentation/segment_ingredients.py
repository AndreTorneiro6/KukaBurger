import cv2
import json
import numpy as np
import requests

# URL for the video feed
url = 'http://172.21.84.101:8080/shot.jpg'


# Function for segmenting ingredients in the image
def segmentation(img, ingredient):
    # Load HSV color ranges for segmentation
    hsv_ingredients_ranges = json.load(open('/home/raspad/Desktop/KukaCooker/segmentation/colors_range.json'))

    # Convert image to HSV color space
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    result = img.copy()

    # Define lower and upper HSV thresholds for the specified ingredient
    lower_range = np.array([hsv_ingredients_ranges[ingredient]['Hmin'], hsv_ingredients_ranges[ingredient]['Smin'],
                            hsv_ingredients_ranges[ingredient]['Vmin']], np.uint8)
    upper_range = np.array([hsv_ingredients_ranges[ingredient]['Hmax'], hsv_ingredients_ranges[ingredient]['Smax'],
                            hsv_ingredients_ranges[ingredient]['Vmax']], np.uint8)

    # Create a mask using the specified thresholds
    mask = cv2.inRange(hsv_image, lower_range, upper_range)

    # Perform dilation and erosion to refine the mask
    kernel = np.ones((13, 13), np.uint8)
    img_dilation = cv2.dilate(mask, kernel, iterations=1)
    kernel = np.ones((15, 15), np.uint8)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

    # Bitwise AND operation to apply the mask to the original image
    result = cv2.bitwise_and(result, result, mask=img_erosion)

    # Find contours of the segmented regions
    contours, hierarchy = cv2.findContours(img_erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a blank image for drawing contours
    blank = np.zeros(img_erosion.shape[:2], dtype='uint8')
    cv2.drawContours(blank, contours, -1, (255, 0, 0), 1)

    # Iterate through contours
    for c in contours:
        if cv2.contourArea(c) > 200:
            _, y, _, _ = cv2.boundingRect(c)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centroid = (cX, cY)
            else:
                cX, cY = 0, 0
            cv2.circle(result, (cX, cY), 5, (255, 255, 255), -1)
            cv2.putText(result, "centroid", (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return centroid, y


# Function to index items and convert pixel coordinates to mm
def index_items(centroids, img):
    tuplas_ordenadas = sorted(centroids, key=lambda tup: tup[0][1])
    data = {}
    for index, (coord, ingredient, y) in enumerate(tuplas_ordenadas):
        data[ingredient] = {"index": index + 1, "X_coord": coord[0], "Y_coord": coord[1], 'Top': y}
    draw_image_ordered(img, data)
    top_value = next((v['Top'] for k, v in data.items() if v['index'] == 1))
    for key, values in data.items():
        values['Y_coord'] = convert_pixel_mm(values['Y_coord'] - top_value)
    return data


# Function to convert pixel coordinates to mm
def convert_pixel_mm(coord):
    return coord * 1.28


# Function to draw numbered circles and descriptions on the image
def draw_image_ordered(img, data):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    for idx, ingredient in enumerate(data):
        cv2.circle(img, (int(data[ingredient]['X_coord']), int(data[ingredient]['Y_coord'])), 10, (0, 255, 0), -1)
        number_text = str(data[ingredient]['index'])
        cv2.putText(img, number_text, (int(data[ingredient]['X_coord']) - 5, int(data[ingredient]['Y_coord']) + 15),
                    font, font_scale, (0, 0, 0), font_thickness)
        cv2.putText(img, f"{data[ingredient]['index']}: {ingredient.replace('HSVRange', '')}",
                    (10, 30 * (int(data[ingredient]['index']) + 1) + 30), font, font_scale, (0, 0, 0), font_thickness)
    cv2.imwrite("output_image.jpg", img)


# Main function
if __name__ == '__main__':
    values = list()
    while (True):
        # Capture the video frame
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)

        ingredients = ['tomatoHSVRange', 'breadBHSVRange', 'breadTHSVRange', 'cheeseHSVRange', 'burgerHSVRange',
                       'onionHSVRange', 'lettuceHSVRange']
        for ingredient in ingredients:
            centroid, y = segmentation(img, ingredient)
            values.append((centroid, ingredient, y))
        index_items(values, img)
        break
    cv2.destroyAllWindows()
