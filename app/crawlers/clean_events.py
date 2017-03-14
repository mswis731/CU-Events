from app import app, mysql
import datetime

def clean_events():
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.callproc('CleanEvents')
	connection.commit()


if __name__ == "__main__":
	clean_events();

