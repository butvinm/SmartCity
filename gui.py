from kivy.clock import Clock
from kivymd.app import MDApp

from widgets.mainwidget import MainWidget


class Application(MDApp):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def build(self) -> MainWidget:
		Clock.max_iteration = 100000
		self.title = 'SafeCity'
		self.main_widget = MainWidget()
		return self.main_widget


if __name__ == '__main__':
	Application().run()
