from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField


class DialogContent(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.size_hint = (1, None)
		self.height = dp('150')
		box_layout = BoxLayout(orientation='vertical')
		box_layout.pos_hint = {'x': 0, 'y': 0}
		self.add_widget(box_layout)
		self.x_field = MDTextField()
		self.x_field.hint_text = 'X'
		self.y_field = MDTextField()
		self.y_field.hint_text = 'Y'
		self.z_field = MDTextField()
		self.z_field.hint_text = 'Z'
		box_layout.add_widget(self.x_field)
		box_layout.add_widget(self.y_field)
		box_layout.add_widget(self.z_field)
