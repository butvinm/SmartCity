from typing import Iterable
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance

from database import db

SIGN_MIN_SIZE = 10000
SIGN_MAX_SIZE = 30000
SIGN_MIN_RATIO = 4.1
SIGN_MAX_RATIO = 4.5
HSV_MIN = np.array((0, 77, 17), np.uint8)
HSV_MAX = np.array((208, 255, 255), np.uint8)


def get_bad_people() -> list[tuple[int, str]]:
	headers, data, imgs = db.get_table_data('people')
	return [(i, ' '.join(info[:3])) for i, info in enumerate(data) if info[-1] == 'В розыске']


def get_bad_cars() -> list[tuple[str, str]]:
	headers, data, imgs = db.get_table_data('offences')
	return [(info[4], info[5]) for info in data]


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

	numbers = img.crop((
		img.width * 0.18, img.height * 0.08,
		img.width * 0.5, img.height * 0.9
	))
	numbers = extend_image(numbers)

	left_chars = img.crop((
		img.width * 0.05, img.height * 0.08,
		img.width * 0.18, img.height * 0.9
	))
	right_chars = img.crop((
		img.width * 0.5, img.height * 0.08,
		img.width * 0.73, img.height * 0.9
	))
	template = Image.new(
		'RGB',
		(left_chars.width + right_chars.width, left_chars.height),
		(255, 255, 255)
	)
	template.paste(left_chars, (0, 0))
	template.paste(right_chars, (left_chars.width, 0))
	chars = extend_image(template)

	region = img.crop((
		img.width * 0.78, img.height * 0.08,
		img.width * 0.96, img.height * 0.65
	))
	region = extend_image(region)
	return left_chars, numbers, right_chars, region


def get_sign_str(fragments: Iterable[Image.Image]) -> str:
	left_chars, numbers, right_chars, region = fragments

	left_chars_str = pytesseract.image_to_string(left_chars).upper()
	numbers_str = pytesseract.image_to_string(numbers, config='digits')
	right_chars_str = pytesseract.image_to_string(right_chars).upper()
	region_str = pytesseract.image_to_string(region, config='digits')
	return left_chars_str + numbers_str + right_chars_str + region_str


def get_sign_rect(img: np.array, rect: tuple[tuple, tuple]) -> np.array:
	box = cv2.boxPoints(rect)
	box = np.int0(box)
	W = rect[1][0]
	H = rect[1][1]

	Xs = [i[0] for i in box]
	Ys = [i[1] for i in box]
	x1, y1 = min(Xs), min(Ys)
	x2, y2 = max(Xs), max(Ys)

	angle = rect[2]
	angle += 90 if angle < -45 else -90

	center = ((x1 + x2) / 2, (y1 + y2) / 2)
	size = (x2 - x1, y2 - y1)
	matrix = cv2.getRotationMatrix2D((size[0] / 2, size[1] / 2), angle, 1.0)
	cropped = cv2.getRectSubPix(img, size, center)
	cropped = cv2.warpAffine(cropped, matrix, size)
	cropped_w = H if H > W else W
	cropped_h = H if H < W else W
	rotated = cv2.getRectSubPix(
            cropped,
            (int(cropped_w), int(cropped_h)),
            (size[0] / 2, size[1] / 2)
	)
	return rotated


def get_signs(img: np.array) -> list[tuple[str, tuple]]:
	'''
	Return list of tuples with sign number in format "A111AA22" and rectangle
	'''
	signs = []
	img = cv2.medianBlur(img, 5, 0)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(hsv, np.array(HSV_MIN, HSV_MAX)
	contours0, hierarchy=cv2.findContours(
		thresh.copy(),
		cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE
	)

	for cnt in contours0:
		rect=cv2.minAreaRect(cnt)
		area=int(rect[1][0] * rect[1][1])
		ratio=max(
			rect[1][1] / rect[1][0],
			rect[1][0] / rect[1][1]
		) if area else 0

		if ((SIGN_MIN_SIZE < area < SIGN_MAX_SIZE) and
                        (SIGN_MIN_RATIO < ratio < SIGN_MIN_RATIO)):
			sign=get_sign_rect(img, rect)
			pil_img=Image.fromarray(cv2.cvtColor(sign, cv2.COLOR_BGR2RGB))
			fragments=fragmentate_sing(pil_img)
			sign_str=get_sign_str(fragments)
			signs += [(sign_str, rect)]

	return signs
