import cv2
import numpy as np

(76, 0, 0)
(255, 255, 105)
img = cv2.imread('database/test_signs_image.png')
cv2.namedWindow('HSV')
cv2.createTrackbar('min_H', 'HSV', 0, 255, lambda value: value)
cv2.createTrackbar('min_S', 'HSV', 0, 255, lambda value: value)
cv2.createTrackbar('min_V', 'HSV', 0, 255, lambda value: value)
cv2.createTrackbar('max_H', 'HSV', 0, 255, lambda value: value)
cv2.createTrackbar('max_S', 'HSV', 0, 255, lambda value: value)
cv2.createTrackbar('max_V', 'HSV', 0, 255, lambda value: value)

while 1:
	min_h = cv2.getTrackbarPos('min_H', 'HSV')
	min_s = cv2.getTrackbarPos('min_S', 'HSV')
	min_v = cv2.getTrackbarPos('min_V', 'HSV')
	max_h = cv2.getTrackbarPos('max_H', 'HSV')
	max_s = cv2.getTrackbarPos('max_S', 'HSV')
	max_v = cv2.getTrackbarPos('max_V', 'HSV')
	print(min_h)
	min_hsv = np.array([min_h, min_s, min_v], np.uint8)
	max_hsv = np.array([max_h, max_s, max_v], np.uint8)

	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(hsv, min_hsv, max_hsv)
	cv2.imshow('2', thresh)
	cv2.imshow('1', hsv)
	if cv2.waitKey(5) == 27:
		break

cv2.destroyAllWindows()
