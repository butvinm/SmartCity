from functools import partial

from database.db import get_table_data
from kivy.core.window import Keyboard, Window
from kivy.properties import ObservableList
from kivymd.uix.boxlayout import MDBoxLayout
from pioneer_sdk import Pioneer

from widgets.sidebar import SideBar
from widgets.sidebutton import SideButton
from widgets.sidecheckbox import SideCheckbox
from widgets.universalframe import UniversalFrame


class MainWidget(MDBoxLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.frame = UniversalFrame()
		self.add_widget(self.frame)

		self.checkboxes = {
			'faces': SideCheckbox('faces'),
			'signs': SideCheckbox('signs'),
		}
		self.btns_data = {
                    'Connect drone': self.act_drone_connect,
               	    'Start': self.act_drone_start,
                    'Patrolling': self.act_drone_patrolling,
                    'Land': self.act_drone_land,
                    'Test': self.act_drone_test,
                    'People DB': partial(self.act_dbview, 'people'),
                    'Cars DB': partial(self.act_dbview, 'cars'),
		}
		self.sidebar = SideBar(self.btns_data, self.checkboxes)
		self.add_widget(self.sidebar)

		self.drone = None
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

	def act_drone_connect(self, btn: SideButton = None):
		if self.drone is None:
			self.drone = Pioneer(logger=False)

	def act_drone_start(self, btn: SideButton = None):
		if self.drone is not None:
			print('Drone has been started')
			self.drone.arm()
			mode = ('signs' if self.checkboxes['signs'].checked else '') + \
                            ('faces' if self.checkboxes['faces'].checked else '')
			self.frame.start_stream(self.drone, mode)

	def act_drone_patrolling(self, btn: SideButton = None):
		if self.drone is not None:
			print('Drone begin patrolling')
			self.drone.takeoff()
			self.drone.go_to_local_point(x=0, y=0, z=0.5, yaw=0)
			self.drone.go_to_local_point(x=0, y=1.5, z=0.5, yaw=0)
			# self.drone.go_to_local_point(x=0, y=2, z=0.7, yaw=math.radians(180))
			# self.drone.go_to_local_point(x=0, y=0, z=0.7, yaw=math.radians(180))
			# self.drone.go_to_local_point(x=0, y=0, z=0, yaw=math.radians(180))
			print('Patrolling is finished')

	def act_drone_land(self, btn: SideButton = None):
		if self.drone is not None:
			print('Drone is landing')
			self.drone.land()
			self.drone.disarm()
			self.frame.stop_stream()

	def act_drone_test(self, btn: SideButton = None):
		self.frame.start_stream(self.drone, 'signs')

	def act_dbview(self, tablename: str, btn: SideButton = None):
		headers, data, imgs = get_table_data(tablename)
		self.frame.show_db(headers, data, imgs)

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard: Keyboard, keycode: tuple, text: str, modifiers: ObservableList):
		if keycode[1].isdigit():
			try:
				tuple(self.btns_data.values())[int(keycode[1]) - 1]()
			except IndexError:
				pass
		return True
