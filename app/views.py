from flask import render_template
from app import app, mysql
from app.crawlers.eventful import crawl as eventful_crawl
import sys

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/eventcreate')
def event_create():
	return render_template('eventcreate.html')

@app.route('/signUp')
def sign_up():
    return render_template('signUp.html')

@app.route('/browse')
def browse():
    return render_template('browse.html')

@app.route('/music/')
def music():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM Category")
	result = cursor.fetchall()
	categories = [row[0] for row in result]
	cursor.close()
	return render_template('browse.html', categories=categories, result=result)

@app.route('/browse')
def get_types():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	result = cursor.fetchall()
	types = [row[0] for row in result]
	cursor.close()
	return render_template('browse.html', types=types, result=result)

@app.route('/<category>')
def find_cat(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM Event WHERE (name, startDate, startTime) IN (SELECT eventName, eventStartDate, eventStartTime FROM HasCategory WHERE categoryName='{}')".format(category))
	events = [dict(name=row[0],
                   description=row[1],
                   building=row[2],
                   addrAndStreet=row[3],
                   city=row[4],
                   zipcode=row[5],
                   startDate=row[6],
                   startTime=row[7],
                   endDate=row[8],
                   endTime=row[9],
                   lowPrice=row[10],
                   highPrice=row[11],
                   nonUserViews=row[12]) for row in cursor.fetchall()]

	return render_template('category.html', events=events)

@app.route('/crawl')
def crawl():
	return eventful_crawl()


