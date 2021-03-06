from flask import Flask
from flaskext.mysql import MySQL
import os

db_user = None
db_password = None
db_name = None
db_host = None

# UPLOAD_FOLDER = "/project411/CU-Events/app/event_photos"

try:
	import app.secret
	db_user = secret.user
	db_password = secret.password
	db_name = secret.db
	db_host = secret.host
except ImportError:
	url = os.environ['DATABASE_URL']
	url_1 = url.split('/')
	url_2 = url_1[2].split('@')
	url_3 = url_2[0].split(':')
	
	db_user = url_3[0]
	db_password = url_3[1]
	db_name = url_1[3].split('?')[0]
	db_host = url_2[1]
	
app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomkey12309034212348'

app.config['MYSQL_DATABASE_USER'] = db_user
app.config['MYSQL_DATABASE_PASSWORD'] = db_password
app.config['MYSQL_DATABASE_DB'] = db_name
app.config['MYSQL_DATABASE_HOST'] = db_host
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL()
mysql.init_app(app)

GMAPS_KEY = 'AIzaSyCwQgKvuUKzqEkWbNs8VjlHHMkDYri7bKs'

from app import views
