import re
from time import time
from concurrent.futures import ThreadPoolExecutor
from weakref import ref

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance


SIGN_MIN_AREA = 40000
SIGN_MAX_AREA = 80000
SIGN_MIN_RATIO = 4
SIGN_MAX_RATIO = 6
HSV_MIN = np.array((39, 18, 135), np.uint8)
HSV_MAX = np.array((255, 255, 255), np.uint8)


def set_hsv(path: str = 'database/test_signs_image.png'):
	img = cv2.imread(path)
	cv2.namedWindow('HSV')
	trackbars_names = ['min_H', 'min_S', 'min_V', 'max_H', 'max_S', 'max_V']
	for name in trackbars_names:
		cv2.createTrackbar(name, 'HSV', 0, 255, lambda value: value)

	while 1:
		min_h = cv2.getTrackbarPos('min_H', 'HSV')
		min_s = cv2.getTrackbarPos('min_S', 'HSV')
		min_v = cv2.getTrackbarPos('min_V', 'HSV')
		max_h = cv2.getTrackbarPos('max_H', 'HSV')
		max_s = cv2.getTrackbarPos('max_S', 'HSV')
		max_v = cv2.getTrackbarPos('max_V', 'HSV')
		min_hsv = np.array([min_h, min_s, min_v], np.uint8)
		max_hsv = np.array([max_h, max_s, max_v], np.uint8)

		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		thresh = cv2.inRange(hsv, min_hsv, max_hsv)
		cv2.imshow('2', thresh)
		cv2.imshow('1', hsv)
		if cv2.waitKey(5) == 27:
			break
	
	print(min_hsv)
	print(max_hsv)
	cv2.destroyAllWindows()


def extend_image(img: Image.Image, value: float = 2.0) -> Image.Image:
	extended = Image.new(
		'RGB',
		(round(img.width * value), round(img.height * value)),
		(255, 255, 255)
	)
	extended.paste(
		img,
		(extended.width // 2 - img.width // 2,
		 extended.height // 2 - img.height // 2
		 )
	)
	return extended


def refragmentate_sing(img: Image.Image) -> tuple[Image.Image]:
	img = ImageEnhance.Contrast(img).enhance(10)
	img = ImageEnhance.Sharpness(img).enhance(5)
	img = img.convert('L').point(lambda x: 255 if x > 120 else 0, mode='1')

	left_chars = img.crop((
		img.width * 0.05, img.height * 0.26,
		img.width * 0.18, img.height * 0.88
	))
	right_chars = img.crop((
		img.width * 0.5, img.height * 0.25,
		img.width * 0.73, img.height * 0.88
	))
	numbers = img.crop((
		img.width * 0.18, img.height * 0.1,
		img.width * 0.5, img.height * 0.88
	))
	numbers = numbers.resize((
		round(numbers.width * 0.75),
		round(numbers.height * 0.75)
	))
	region = img.crop((
		img.width * 0.78, img.height * 0.1,
		img.width * 0.96, img.height * 0.58
	))
	refrag_sign = [left_chars, right_chars, numbers, region]
	template = Image.new(
		'RGB',
		(sum(f.width for f in refrag_sign), max(f.height for f in refrag_sign)),
		(255, 255, 255)
	)
	for i in range(4):
		template.paste(
			refrag_sign[i],
			(sum(f.width for f in refrag_sign[:i]), 0)
		)
	refrag_sign = extend_image(template)
	return refrag_sign


def get_sign_str(refrag_sign: Image.Image) -> str:
	sign_str = pytesseract.image_to_string(
		refrag_sign, config='opt -fopenmp').upper()
	sign_str = re.sub(r'\W', '', sign_str)
	if len(sign_str) not in (8, 9):
		return None
	chrs = sign_str[:3]
	if re.search('\D+', chrs) is None:
		return None
	nums = sign_str[3:6]
	if re.search('\d+', nums) is None:
		return None
	reg = sign_str[6:]
	sign_str = chrs[0] + nums + chrs[1:] + reg
	return sign_str


def get_sign_rect(img: np.array, rect: tuple[tuple, tuple]) -> np.array:
	box = np.int0(cv2.boxPoints(rect))
	W = rect[1][0]
	H = rect[1][1]

	Xs = [i[0] for i in box]
	Ys = [i[1] for i in box]
	x1, y1 = min(Xs), min(Ys)
	x2, y2 = max(Xs), max(Ys)

	angle = rect[2]
	if angle < -45:
		angle += 90
	elif angle > 45:
		angle -= 90

	center = ((x1 + x2) / 2, (y1 + y2) / 2)
	size = (x2 - x1, y2 - y1)
	matrix = cv2.getRotationMatrix2D((size[0] / 2, size[1] / 2), angle, 1.0)
	cropped = cv2.getRectSubPix(img, size, center)
	cropped = cv2.warpAffine(cropped, matrix, size)
	cropped_w, cropped_h = max(H, W), min(H, W)
	rotated = cv2.getRectSubPix(
            cropped,
            (int(cropped_w), int(cropped_h)),
            (size[0] / 2, size[1] / 2)
	)
	return rotated


def get_relative_rects(contours: list[np.array]) -> list[tuple]:
	rects = []
	for contour in contours:
		rect = cv2.minAreaRect(contour)
		area = int(rect[1][0] * rect[1][1])
		if not (SIGN_MIN_AREA < area < SIGN_MAX_AREA):
			continue
		ratio = rect[1][1] / rect[1][0]
		ratio = max(ratio, 1 / ratio)
		if not (SIGN_MIN_RATIO < ratio < SIGN_MAX_RATIO):
			continue
		rects += [rect]
	return rects


def get_sign(img: np.array, rect: tuple[tuple, tuple]) -> str:
	sign = get_sign_rect(img, rect)
	pil_img = Image.fromarray(cv2.cvtColor(sign, cv2.COLOR_BGR2RGB))
	refrag_sign = refragmentate_sing(pil_img)
	sign_str = get_sign_str(refrag_sign)
	if sign_str:
		return sign_str, rect
	return None


def signs_from_frame(img: np.array) -> list[tuple[str, tuple]]:
	img = cv2.medianBlur(img, 5, 0)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(hsv, HSV_MIN, HSV_MAX)
	cv2.imshow('2', thresh)
	contours, _ = cv2.findContours(
		thresh.copy(),
		cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE
	)
	rects = get_relative_rects(contours)
	workers = len(rects)
	if not workers:
		return []
	with ThreadPoolExecutor(workers) as executor:
		signs = executor.map(
			get_sign,
			[img for _ in range(workers)],
			rects
		)
	return [sign for sign in signs if sign is not None]


def signs_from_file(file_path: str) -> list[tuple[str, tuple]]:
	img = cv2.imread(file_path)
	return signs_from_frame(img)


if __name__ == '__main__':
	# st = time()
	# signs = signs_from_file('database/test_signs_image.png')
	# print('Full time:', time() - st)
	# print(signs)
	set_hsv('database/test_signs_image.png')
