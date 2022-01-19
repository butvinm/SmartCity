import csv
import os
import sqlite3
from venv import create

DBPATH = 'database/database.db'


def table_from_csv(csvpath: str, table_name: str):
	with open(csvpath, 'r') as f:
		rows = [row for row in csv.reader(f, delimiter=';')]
	headers = rows[0]
	data = rows[1:]

	con = sqlite3.connect(DBPATH)
	cur = con.cursor()
	cur.execute(f'DROP TABLE IF EXISTS {table_name}')
	query = f'''CREATE TABLE {table_name} ("{'", "'.join(headers)}")'''
	cur.execute(query)

	for row in data:
		query = f'''INSERT INTO {table_name} VALUES ("{'", "'.join(row)}")'''
		cur.execute(query)

	con.commit()
	con.close()


def get_table_data(table_name: str) -> tuple[list]:
	con = sqlite3.connect(DBPATH)
	cur = con.cursor()
	query = f'SELECT * from {table_name}'
	result = cur.execute(query)
	headers = [d[0] for d in result.description]
	data = [d for d in result]

	imgs_folder = os.path.join(os.getcwd(), 'database', f'{table_name}_imgs')
	if os.path.exists(imgs_folder):
		imgs = [os.path.join(imgs_folder, path) for path in os.listdir(imgs_folder)]
	else:
		imgs = None

	return headers, data, imgs

