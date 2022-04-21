import io

import numpy as np
from database.db import get_bad_cars, get_bad_people
# from faces_recognize import faces_from_frame
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from pioneer_sdk import Pioneer
from signs_recognize import signs_from_frame
# from stream_utils import draw_face, draw_sign, frame_to_cv2img, img_to_buf


class StreamView(Image):
	size_hint = 1, 1

	def __init__(self, drone: Pioneer, mode: str, **kwargs):
		super().__init__(**kwargs)
		self._mode = mode
		self._frame_counter = 0
		self._vec_k = 0.1
		self._bad_cars = get_bad_cars()
		self._bad_people = get_bad_people()
		self._last_frame = None
		self._signs = []
		self._faces = []
		self.drone = drone

		if 'signs' in self._mode:
			Clock.schedule_interval(self._update_signs, timeout=0.5)
		if 'faces' in self._mode:
			Clock.schedule_interval(self._update_faces, timeout=1)

		Clock.schedule_interval(
			self._update_frame,
			timeout=0.05
		)

	def _frame_process_signs(self) -> np.array:
		img = self._last_frame[::]
		for sign in self._signs:
			offence = self._bad_cars.get(sign[0], None)
			if offence is not None:
				img = draw_sign(
					img,
					offence,
					sign[1],
					(0, self._frame_counter * self._vec_k)
				)
		return img

	def _frame_process_faces(self) -> np.array:
		img = self._last_frame[::]
		for data, rect in self._faces:
			name = ' '.join(data[:3]) if data is not None else ''
			img = draw_face(img, name, rect, 'r' if data is not None else 'g')
		return img

	def _bytes_to_frame(self, image_bytes: bytes) -> CoreImage:
		buf = io.BytesIO(image_bytes)
		cim = CoreImage(buf, ext='png')
		return cim

	def _update_signs(self, *args):
		if self._last_frame is not None:
			self._signs = signs_from_frame(self._last_frame)

	def _update_faces(self, *args):
		if self._last_frame is not None:
			self._faces = faces_from_frame(self._last_frame)

	def _update_frame(self, *args):
		camera_frame = self.drone.get_raw_video_frame()
		self._last_frame = frame_to_cv2img(camera_frame)
		if 'signs' in self._mode:
			img = self._frame_process_signs()
		if 'faces' in self._mode:
			img = self._frame_process_faces()

		img_buf = img_to_buf(img)
		frame = self._bytes_to_frame(img_buf)
		self.texture = frame.texture
