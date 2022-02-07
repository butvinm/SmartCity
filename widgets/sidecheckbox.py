from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox


class SideCheckbox(MDBoxLayout):
	def __init__(self, label: str, **kwargs):
		super().__init__(**kwargs)
		self.add_widget(MDCheckbox(size_hint=(0.5, 1)))
		self.add_widget(MDLabel(text=label))
	
	@property
	def checked(self) -> bool:
		return self.children[1].state == 'down'
