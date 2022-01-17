from typing import Callable
from kivymd.uix.boxlayout import MDBoxLayout
from widgets.sidebutton import SideButton


class SideBar(MDBoxLayout):
	size_hint = 0.3, 1
	orientation = 'vertical'
	spacing = 20
	padding = (20, 20, 20, 20)

	def __init__(self, btns_data: dict[str, Callable], **kwargs):
		super().__init__(**kwargs)
		for label, action in btns_data.items():
			self.add_widget(SideButton(label, action))
