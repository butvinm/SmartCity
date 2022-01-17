from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.floatlayout import MDFloatLayout


class SideButton(MDFloatLayout):
	def __init__(self, label, action, **kwargs):
		super().__init__(**kwargs)
		self.add_widget(MDRectangleFlatButton(
			text=label, 
			pos_hint={'x': 0, 'y': 0}, 
			size_hint=(1, 1),
			on_release=action
		))
	