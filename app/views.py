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

@app.route('/emptypage')
def empty():
    return render_template('emptypage.html')

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
def browse():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	print(categories)
	cursor.execute("SELECT * FROM Event")
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
	cursor.close()
	return render_template('browse.html', categories=categories, types=types, events=events)

@app.route('/browse/category/<category>')
def event_(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
	cursor.execute("SELECT * FROM Event WHERE (id) IN (SELECT eventID FROM HasCategory WHERE categoryName='{}')".format(category))
	events = [dict(title=row[1],
                   description=row[2],
                   building=row[3],
                   addrAndStreet=row[4],
                   city=row[5],
                   zipcode=row[6],
                   startDate=row[7],
                   startTime=row[8],
                   endDate=row[9],
                   endTime=row[10],
                   lowPrice=row[11],
                   highPrice=row[12],
                   nonUserViews=row[13]) for row in cursor.fetchall()]
	return render_template('temp.html', events=events)

@app.route('/crawl')
def crawl():
	return eventful_crawl()

	return render_template('eventlist.html', events=events)

@app.route('/browse/type/<e_type>')
def event_type(e_type):
	connection = mysql.get_db()
	cursor = connection.cursor()
	e_type = " ".join([ (word.capitalize() if word != 'and' else word) for word in e_type.split('-') ])
	cursor.execute("SELECT * FROM Event WHERE (id) IN (SELECT eventID FROM HasEventType WHERE eventType='{}')".format(e_type))
	events = [dict(title=row[1],
                   description=row[2],
                   building=row[3],
                   addrAndStreet=row[4],
                   city=row[5],
                   zipcode=row[6],
                   startDate=row[7],
                   startTime=row[8],
                   endDate=row[9],
                   endTime=row[10],
                   lowPrice=row[11],
                   highPrice=row[12],
                   nonUserViews=row[13]) for row in cursor.fetchall()]

	return render_template('temp.html', events=events)


@app.route('/browse/free')
def find_free():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM Event WHERE lowPrice IS NULL AND highPrice IS NULL")
	frees = [dict(title=row[1],
                   description=row[2],
                   building=row[3],
                   addrAndStreet=row[4],
                   city=row[5],
                   zipcode=row[6],
                   startDate=row[7],
                   startTime=row[8],
                   endDate=row[9],
                   endTime=row[10],
                   lowPrice=row[11],
                   highPrice=row[12],
                   nonUserViews=row[13]) for row in cursor.fetchall()]


	return render_template('temp.html', frees=frees)

@app.route('/browse/delete/<delete_id>')
def remove_event(delete_id):
      connection = mysql.get_db()
      cursor = connection.cursor()
      cursor.execute("DELETE FROM Event WHERE name = 'delete_id'")
      #cursor.execute("SELECT * FROM Event WHERE (name, startDate, startTime) IN (SELECT eventName, eventStartDate, eventStartTime FROM HasCategory WHERE categoryName='{}')".format(category))
      # events = [dict(name=row[0],
      #             description=row[1],
      #              building=row[2],
      #              addrAndStreet=row[3],
      #              city=row[4],
      #              zipcode=row[5],
      #              startDate=row[6],
      #              startTime=row[7],
      #              endDate=row[8],
      #              endTime=row[9],
      #              lowPrice=row[10],
      #              highPrice=row[11],
      #              nonUserViews=row[12]) for row in cursor.fetchall()]
      return render_template('index.html')
