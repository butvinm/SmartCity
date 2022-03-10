from reprlib import Repr
from time import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from database.db import get_bad_cars, get_bad_people
from signs_recognize import signs_from_frame
from faces_recognize import faces_from_frame


TEXT_ARGS = (cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
FONT = ImageFont.truetype('./database/bahnschrift.ttf', 28)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
COLORS = {'r': RED, 'g': GREEN, 'b': BLUE}


def put_text(
	img: np.array, 
	text: str, 
	pos: tuple[float, float], 
	max_chars: int = 40,
	color: tuple[int, int, int] = RED
) -> np.array:

	img_pil = Image.fromarray(img)
	draw = ImageDraw.Draw(img_pil)
	r = Repr()
	r.maxstring = max_chars
	draw.text(pos, r.repr(text), font=FONT, fill=RED)
	img = np.array(img_pil)
	return img


def draw_sign(
	img: np.array,
	label: str,
	rect: tuple,
	vec: tuple[float, float] = (0, 0),
	c: str = 'r'
) -> np.array:
	color = COLORS[c]
	offset = np.array(vec, 'float')
	# draw sign bordered rectangle
	box = np.int0(cv2.boxPoints(rect) + offset)
	img = cv2.drawContours(img, [box], 0, color, 2)
	# put label in image
	pos = np.array(rect[0], dtype='float')
	pos += offset
	pos[0] -= (box[:, 0].max() - box[:, 0].min()) / 2
	pos[1] += (box[:, 1].max() - box[:, 1].min()) / 2
	img = put_text(img, label, pos, color=color)
	return img


def draw_face(
	img: np.array, 
	label: str, 
	rect: tuple, 
	c: str = 'r'
) -> np.array:
	color = COLORS[c]
	top, right, bottom, left = rect
	img = cv2.rectangle(img, (left, top), (right, bottom), color, 2)
	img = put_text(img, label, (left, bottom), color=color)
	return img


def frame_to_cv2img(frame: bytes) -> np.array:
	img = cv2.imdecode(
            np.frombuffer(frame, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )
	return img


def img_to_buf(img: np.array) -> bytes:
	_, buf = cv2.imencode('.jpg', img)
	return buf


if __name__ == '__main__':
	# bad_people = get_bad_people()
	# # [print(item) for item in bad_people]
	# img = cv2.imread('database/test_face_1.jpg')
	# faces = faces_from_frame(img)
	# for data, rect in faces:
	# 	top, right, bottom, left = rect
	# 	img = cv2.rectangle(img, (left, top), (right, bottom), RED, 2)
	# 	img = put_text(img, ' '.join(data[:3]), (left, bottom))
	
	# img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
	# cv2.imshow('Frame', img)
	# cv2.waitKey()
	bad_cars = get_bad_cars()
	img = cv2.imread('./database/test_signs_image.png')
	signs = signs_from_frame(img)
	print(signs)
	for sign in signs:
		offence = bad_cars.get(sign[0], None)
		if offence is not None:
			img = draw_sign(
				img,
				offence,
				sign[1]
			)
	cv2.imshow('1', img)
	cv2.waitKey()