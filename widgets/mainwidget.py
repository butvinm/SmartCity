from functools import partial

from database.db import get_table_data
from kivy.core.window import Keyboard, Window
from kivy.properties import ObservableList
from kivymd.uix.boxlayout import MDBoxLayout
from pioneer_sdk import Pioneer

from widgets.sidebar import SideBar
from widgets.sidebutton import SideButton
from widgets.universalframe import UniversalFrame


class MainWidget(MDBoxLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		# self.drone = Pioneer()
		self.frame = UniversalFrame()
		self.add_widget(self.frame)

		btns_data = {
                    'Start': self.act_drone_start,
                    'Patrolling': self.act_drone_patrolling,
                    'Back': self.act_drone_back,
                    'Test': self.act_dron_test,
                    'People DB': partial(self.act_dbview, 'people'),
                    'Cars DB': partial(self.act_dbview, 'cars'),
                    'Offences': partial(self.act_dbview, 'offences')
		}
		self.sidebar = SideBar(btns_data)
		self.add_widget(self.sidebar)

		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

	def act_drone_start(self, btn: SideButton = None):
		print('Drone started')
		self.drone.arm()
		self.frame.start_stream()

	def act_drone_patrolling(self, btn: SideButton = None):
		print('Drone begin patrolling')
		self.drone.takeoff()
		self.drone.go_to_local_point(x=0, y=2, z=0.7, yaw=0)

	def act_drone_back(self, btn: SideButton = None):
		print('Drone come back')
		self.drone.go_to_local_point(x=0, y=0, z=0.7, yaw=0)
		self.drone.land()

	def act_dron_test(self, btn: SideButton = None):
		print('Test drone')
		self.drone.arm()

	def act_dbview(self, tablename: str, btn: SideButton = None):
		headers, data, imgs = get_table_data(tablename)
		self.frame.show_db(headers, data, imgs)

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard: Keyboard, keycode: tuple, text: str, modifiers: ObservableList):
		key_to_act = {
                    '1': self.act_drone_start,
                    '2': self.act_drone_patrolling,
                    '3': self.act_drone_back,
                    '4': self.act_dron_test,
                    '5': partial(self.act_dbview, 'people'),
                    '6': partial(self.act_dbview, 'cars'),
                    '7': partial(self.act_dbview, 'offences')
		}
		if keycode[1] in key_to_act:
			key_to_act[keycode[1]]()

		return True
