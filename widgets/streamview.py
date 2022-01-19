import io

from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.widget import Widget


class StreamView(Image):
	def __init__(self, drone, **kwargs):
		super().__init__(**kwargs)
		self.drone = drone

	def on_kv_post(self, base_widget: Widget):
		self.size_hint = None, None
		self.allow_stretch = True
		self.keep_ratio = False
		self.opacity = 0
		self.nocache = True
		return super().on_kv_post(base_widget)

	def start(self):
		self.update_event = Clock.schedule_interval(self._update_frame, 0.1)

	def stop(self):
		pass

	def _bytes_to_img(self, image_bytes: bytes):
		buf = io.BytesIO(image_bytes)
		cim = CoreImage(buf, ext='jpg')
		return Image(texture=cim.texture)

	def _update_frame(self):
		camera_frame = self.drone.get_raw_video_frame()
		image = self.bytes_to_img(camera_frame)
		self.canvas = image.canvas
