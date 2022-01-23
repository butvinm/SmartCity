import re
from time import time
from typing import Iterable, Iterator

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance


SIGN_MIN_AREA = 10000
SIGN_MAX_AREA = 100000
SIGN_MIN_RATIO = 4
SIGN_MAX_RATIO = 4.5
HSV_MIN = np.array((76, 0, 0), np.uint8)
HSV_MAX = np.array((255, 255, 105), np.uint8)


def extend_image(img: Image.Image) -> Image.Image:
	extended = Image.new(
		'RGB',
		(img.width * 5, img.height * 5),
		(255, 255, 255)
	)
	extended.paste(
		img,
		(extended.width // 2 - img.width // 2,
		 extended.height // 2 - img.height // 2
		 )
	)
	return extended


def fragmentate_sing(img: Image.Image) -> tuple[Image.Image]:
	img = ImageEnhance.Contrast(img).enhance(10)
	img = ImageEnhance.Sharpness(img).enhance(5)
	img = img.convert('L').point(lambda x: 255 if x > 100 else 0, mode='1')

	left_chars = img.crop((
		img.width * 0.05, img.height * 0.1,
		img.width * 0.18, img.height * 0.8
	))
	right_chars = img.crop((
		img.width * 0.5, img.height * 0.1,
		img.width * 0.73, img.height * 0.8
	))
	template = Image.new(
		'RGB',
		(left_chars.width + right_chars.width, left_chars.height),
		(255, 255, 255)
	)
	template.paste(left_chars, (0, 0))
	template.paste(right_chars, (left_chars.width, 0))
	chars = extend_image(template)

	numbers = img.crop((
		img.width * 0.18, img.height * 0.1,
		img.width * 0.5, img.height * 0.8
	))
	numbers = extend_image(numbers)

	region = img.crop((
		img.width * 0.78, img.height * 0.1,
		img.width * 0.96, img.height * 0.55
	))
	region = extend_image(region)

	return chars, numbers, region


def get_sign_str(fragments: Iterable[Image.Image]) -> str:
	pattern = r'\W'
	chars, numbers, region = fragments
	chars_str = pytesseract.image_to_string(chars).upper()
	chars_str = re.sub(pattern, '', chars_str)
	if len(chars_str) != 3:
		return None
	numbers_str = pytesseract.image_to_string(numbers, config='digits')
	numbers_str = re.sub(pattern, '', numbers_str)
	if len(numbers_str) != 3:
		return None
	region_str = pytesseract.image_to_string(region, config='digits')
	region_str = re.sub(pattern, '', region_str)
	if len(region_str) not in (2, 3):
		return None
	sign_str = ''.join([chars_str[0], numbers_str, chars_str[1:], region_str])
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


def get_signs(img: np.array) -> Iterator[tuple[str, tuple]]:
	img = cv2.medianBlur(img, 5, 0)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(hsv, HSV_MIN, HSV_MAX)
	contours0, _ = cv2.findContours(
		thresh.copy(),
		cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE
	)

	for cnt in contours0:
		rect = cv2.minAreaRect(cnt)
		area = int(rect[1][0] * rect[1][1])
		if not (SIGN_MIN_AREA < area < SIGN_MAX_AREA):
			continue

		ratio = rect[1][1] / rect[1][0]
		ratio = max(ratio, 1 / ratio)
		if not (SIGN_MIN_RATIO < ratio < SIGN_MAX_RATIO):
			continue

		sign = get_sign_rect(img, rect)
		pil_img = Image.fromarray(cv2.cvtColor(sign, cv2.COLOR_BGR2RGB))
		fragments = fragmentate_sing(pil_img)
		sign_str = get_sign_str(fragments)
		if sign_str:
			yield (sign_str, rect)


if __name__ == '__main__':
	img = cv2.imread('database/test_signs_image.png')
	st = time()
	signs = get_signs(img).__next__()
	print(time() - st)
	print(signs)
