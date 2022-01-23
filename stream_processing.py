from database import db


def get_bad_people() -> list[tuple[int, str]]:
	headers, data, imgs = db.get_table_data('people')
	return [(i, ' '.join(info[:3])) for i, info in enumerate(data) if info[-1] == 'В розыске']


def get_bad_cars() -> list[tuple[str, str]]:
	headers, data, imgs = db.get_table_data('offences')
	return [(info[4], info[5]) for info in data]


if __name__ == '__main__':
	bad_cars = get_bad_cars()
	[print(item) for item in bad_cars]
	bad_people = get_bad_people()
	[print(item) for item in bad_people]
