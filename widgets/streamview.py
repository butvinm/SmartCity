import io

from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.widget import Widget


class StreamView(Image):	
	size_hint = 1, 1

	def __init__(self, drone, **kwargs):
		super().__init__(**kwargs)
		self.drone = drone
		self.update_trigger = Clock.create_trigger(
			self._update_frame,
			timeout=0.05,
			interval=True
		)

	def on_parent(self, *args):
		if self.parent is not None:
			self.update_trigger()
		else:
			self.update_trigger.close()

	def _bytes_to_img(self, image_bytes: bytes):
		buf = io.BytesIO(image_bytes)
		cim = CoreImage(buf, ext='png')
		return Image(texture=cim.texture)

	def _update_frame(self, *args):
		print('Update frame')
		camera_frame = self.drone.get_raw_video_frame()
		image = self._bytes_to_img(camera_frame)
		self.texture = image.texture