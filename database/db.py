import sqlite3
from sqlite3 import OperationalError
import csv


DBPATH = 'database/database.db'


def table_from_csv(csvpath: str, tablename: str):
	with open(csvpath, 'r') as f:
		rows = [row for row in csv.reader(f, delimiter=';')]
	headers = rows[0]
	data = rows[1:]

	con = sqlite3.connect(DBPATH)
	cur = con.cursor()
	cur.execute(f'DROP TABLE IF EXISTS {tablename}')
	query = f'''CREATE TABLE {tablename} ("{'", "'.join(headers)}")'''
	cur.execute(query)

	for row in data:
		query = f'''INSERT INTO {tablename} VALUES ("{'", "'.join(row)}")'''
		cur.execute(query)

	con.commit()
	con.close()


def get_table_data(tablename: str) -> tuple[list, list]:
	con = sqlite3.connect(DBPATH)
	cur = con.cursor()
	query = f'SELECT * from {tablename}'
	result = cur.execute(query)
	headers = [d[0] for d in result.description]
	data = [d for d in result]
	return headers, data