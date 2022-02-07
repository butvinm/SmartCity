import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
import face_recognition
import cv2
import numpy as np
from database.db import get_bad_people

IMG_SCALE = 0.2


def get_faces(img: np.array) -> tuple[list[np.array]]:
	rgb_img = img[:, :, ::-1]
	rgb_img = cv2.resize(rgb_img, (0, 0), fx=IMG_SCALE, fy=IMG_SCALE)
	locations = face_recognition.face_locations(rgb_img)
	encodings = face_recognition.face_encodings(rgb_img, locations)
	return np.array(locations, 'float'), encodings


def get_known_faces() -> list:
	data, imgs_pathes = get_bad_people()
	infos, faces = [], []
	for info, path in zip(data, imgs_pathes):
		img = cv2.imread(path)
		faces += get_faces(img)[1]
		infos += [info]
	return data, faces


DATA, FACES = get_known_faces()


def match_face(face: np.array) -> list:
	matches = face_recognition.compare_faces(FACES, face)
	return DATA[matches.index(True)] if True in matches else None


def faces_from_frame(img: np.array) -> tuple[list[str], list[np.array]]:
	found_locations, found_encodings = get_faces(img)
	return [
		(match_face(enc), np.int0(loc / IMG_SCALE))
		for loc, enc in zip(found_locations, found_encodings)
	]
