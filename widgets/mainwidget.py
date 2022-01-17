from functools import partial

from database.db import get_table_data
from kivymd.uix.boxlayout import MDBoxLayout

from widgets.sidebar import SideBar
from widgets.sidebutton import SideButton
from widgets.universalframe import UniversalFrame


class MainWidget(MDBoxLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.frame = UniversalFrame(...)
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

	def act_drone_start(self, btn: SideButton):
		print('Drone started')

	def act_drone_patrolling(self, btn: SideButton):
		print('Drone begin patrolling')

	def act_drone_back(self, btn: SideButton):
		print('Drone come back')

	def act_dron_test(self, btn: SideButton):
		print('Test drone')

	def act_dbview(self, tablename: str, btn: SideButton):
		headers, data = get_table_data(tablename)
		self.frame.show_db(headers, data)