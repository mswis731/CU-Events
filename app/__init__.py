from flask import Flask
from flaskext.mysql import MySQL
import app.secret

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = secret.user
app.config['MYSQL_DATABASE_PASSWORD'] = secret.password
app.config['MYSQL_DATABASE_DB'] = secret.db
app.config['MYSQL_DATABASE_HOST'] = secret.host
mysql = MySQL()
mysql.init_app(app)

from app import views
