import io

import numpy as np
from database.db import get_bad_cars, get_bad_people
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from pioneer_sdk import Pioneer
from signs_recognize import signs_from_frame
from stream_utils import draw_sign, frame_to_img, img_to_buf


class StreamView(Image):
	size_hint = 1, 1

	def __init__(self, drone: Pioneer, mode: str, **kwargs):
		super().__init__(**kwargs)
		self._mode = mode
		self._frame_counter = 0
		self._vec_k = 0.1
		
		self.drone = drone
		self.offences = get_bad_cars()
		self.signs = []

		self.update_event = Clock.schedule_interval(
			self._update_frame,
			timeout=0.05
		)
		self.update_event()

	def on_parent(self, *args):
		if self.parent is None:
			self.update_event.cancel()

	def _frame_process_signs(self, img: np.array) -> bytes:
		if self._frame_counter == 15:
			self._frame_counter = 0
			self.signs = signs_from_frame(img)

		for sign in self.signs:
			offence = self.offences.get(sign[0], None)
			if offence is not None:
				img = draw_sign(
					img, 
					offence, 
					sign[1], 
					(0, self._frame_counter * self._vec_k)
				)
		self._frame_counter += 1
		return img_to_buf(img)

	def _bytes_to_frame(self, image_bytes: bytes) -> CoreImage:
		buf = io.BytesIO(image_bytes)
		cim = CoreImage(buf, ext='png')
		return cim

	def _update_frame(self, *args):
		camera_frame = self.drone.get_raw_video_frame()
		img = frame_to_img(camera_frame)

		if self._mode == 'signs':
			img_buf = self._frame_process_signs(img)

		frame = self._bytes_to_frame(img_buf)
		self.texture = frame.texture
