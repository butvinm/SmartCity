from reprlib import repr
from time import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from database.db import get_bad_cars, get_bad_people
from signs_recognize import signs_from_frame

TEXT_ARGS = (cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
FONT = ImageFont.truetype('./database/bahnschrift.ttf', 28)
RED = (0, 0, 255)


def draw_sign(
	img: np.array,
	label: str,
	rect: tuple,
	vec: tuple[float, float] = (0, 0)
) -> np.array:

	offset = np.array(vec, 'float')

	# draw sign bordered rectangle
	box = np.int0(cv2.boxPoints(rect) + offset)
	img = cv2.drawContours(img, [box], 0, RED, 2)

	# put label in image
	img_pil = Image.fromarray(img)
	draw = ImageDraw.Draw(img_pil)

	pos = np.array(rect[0], dtype='float')
	pos += offset
	pos[0] -= (box[:, 0].max() - box[:, 0].min()) / 2
	pos[1] += (box[:, 1].max() - box[:, 1].min()) / 2
	draw.text(pos, repr(label), font=FONT, fill=RED)

	img = np.array(img_pil)
	return img


def frame_to_img(frame: bytes) -> np.array:
	img = cv2.imdecode(
            np.frombuffer(frame, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )
	return img


def img_to_buf(img: np.array) -> bytes:
	_, buf = cv2.imencode('.jpg', img)
	return buf

if __name__ == '__main__':
	bad_cars = get_bad_cars()
	bad_people = get_bad_people()
	[print(item) for item in bad_cars]

	img = cv2.imread('database/test_signs_image.png')
	# signs = signs_from_frame(img)
	
	# for sign in signs:
	# 	offence = bad_cars.get(sign[0], None)
	# 	if offence is not None:
	# 		img = draw_sign(img, offence, sign[1])
	
	cv2.imshow('Frame', img)
	cv2.waitKey()
