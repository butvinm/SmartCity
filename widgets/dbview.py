from kivymd.uix.datatables import MDDataTable, CellRow
from PIL import Image


class DBView(MDDataTable):
	rows_num = 10
	use_pagination = True
	
	def __init__(self, imgs: dict[int, str], **kwargs):
		super().__init__(**kwargs)
		self.imgs = imgs if imgs else []
		self.bind(on_row_press=self._on_row_press)
	
	def _on_row_press(self, instance_table: MDDataTable, instance_cell: CellRow):
		index = instance_cell.index // len(instance_table.column_data)		
		try:
			Image.open(self.imgs[index]).show()
		except KeyError:
			pass