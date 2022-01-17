from kivy.uix.anchorlayout import AnchorLayout
from widgets.videoview import VideoView
from widgets.dbview import DBView


class UniversalFrame(AnchorLayout):
	anchor = 'center'
	padding = (20, 20, 20, 20)

	def __init__(self, drone, **kwargs):
		super().__init__(**kwargs)
		self.drone = drone

	def show_db(self, headers: list, data: list):
		rows_lens = [[len(col) for col in d] for d in [headers] + data]
		cols_widths = [max(c_l) * 2 + 5 for c_l in zip(*rows_lens)]
		self.clear_widgets()
		self.add_widget(DBView(
			column_data=zip(headers, cols_widths),
			row_data=data
		))

