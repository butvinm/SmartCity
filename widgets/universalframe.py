from kivy.uix.anchorlayout import AnchorLayout
from pioneer_sdk.piosdk import Pioneer
from widgets.streamview import StreamView
from widgets.dbview import DBView


class UniversalFrame(AnchorLayout):
	anchor = 'center'
	padding = (20, 20, 20, 20)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def show_db(self, headers: list, data: list, imgs: list):
		rows_lens = [[len(col) for col in d] for d in [headers] + data]
		cols_widths = [max(c_l) * 2 + 5 for c_l in zip(*rows_lens)]
		self.clear_widgets()
		self.add_widget(DBView(
			imgs,
			column_data=zip(headers, cols_widths),
			row_data=data
		))
	
	def start_stream(self, drone: Pioneer):
		pass