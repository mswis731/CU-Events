<<<<<<< HEAD
from flask import Flask, render_template, redirect, url_for, request
from wtforms import Form, TextField, TextAreaField, validators, SelectField
from app import app
=======
from flask import render_template
from app import app, mysql
>>>>>>> 18b22e6522cdf773a951920bdde4c1ce733d3fb8
from app.crawlers.eventful import crawl as eventful_crawl
import sys

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

<<<<<<< HEAD

class ReusableForm(Form):
	title = TextField('Event title', validators=[validators.required()])
	description = TextAreaField('Event description')
	venuename = TextField(id = 'venuename', validators=[validators.required()])
	venueaddr = TextField(id ='venueaddr', validators=[validators.required()])
	venuecity = TextField(id = 'venuecity', validators=[validators.required()])
	venuestate = TextField(id = 'venuestate', validators=[validators.required()])
	venuezip = TextField(id = 'venuezip', validators=[validators.required()])
	eventsmonth = TextField(id = 'eventsmonth', validators=[validators.required()])
	eventsdate = TextField(id = 'eventsdate', validators=[validators.required()])
	eventsyear = TextField(id = 'eventsyear', validators=[validators.required()])
	eventstime = TextField(id = 'eventstime', validators=[validators.required()])
	eventemonth = TextField(id = 'eventemonth', validators=[validators.required()])
	eventedate = TextField(id = 'eventedate', validators=[validators.required()])
	eventeyear = TextField(id = 'eventeyear', validators=[validators.required()])
	eventetime = TextField(id = 'eventetime', validators=[validators.required()])
	price = TextField(id = 'price', validators=[validators.required()])
	category = SelectField(id ='category', choices = ['music', 'sports', 'theatre', 'tech'])
	eventtype = SelectField(id ='eventtype', choices = ['class', 'performance', 'concert', 'presentation'])

	
@app.route('/eventcreate', methods=['GET','POST'])
def signup():
	form = ReusableForm(request.form)
	error = None
	if request.method == 'POST':
		title =  request.form['title']
		description = request.form['description']
		venuename = request.form['venuename']
		address = request.form['venueaddr']
		venuecity = request.form['venuecity']
		venuestate = request.form['venuestate']
		venuezip = request.form['venuezip']
		eventsmonth = request.form['eventsmonth']
		eventsdate = request.form['eventsdate']
		eventsyear = request.form['eventsyear']
		eventstime = request.form['eventstime']
		eventemonth = request.form['eventemonth']
		eventedate = request.form['eventedate']
		eventeyear = request.form['eventeyear']
		eventetime = request.form['eventetime']
		price = request.form['price']
		category = request.form['category']
		eventType = request.form['eventtype']

		if form.validate():
			error = 'Thanks for registering the event' 
		else:
			error = 'Error: Missing Filling a form field'

	return render_template('eventcreate.html', form = form, error=error)
=======
@app.route('/eventcreate')
def event_create():
	return render_template('eventcreate.html')
>>>>>>> 18b22e6522cdf773a951920bdde4c1ce733d3fb8

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
def event_category(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
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
	if (len(events) == 0):
	 	empty = "there are no events to show"
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
	cursor.execute("SELECT * FROM Event WHERE (name, startDate, startTime) IN (SELECT eventName, eventStartDate, eventStartTime FROM HasEventType WHERE eventType='{}')".format(e_type))
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

	return render_template('temp.html', events=events)


@app.route('/browse/free')
def find_free():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM Event WHERE lowPrice IS NULL AND highPrice IS NULL")
	frees = [dict(name=row[0],
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

	return render_template('temp.html', frees=frees)


@app.route('/browse/all')
def all_events():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM Event")
	all_events = [dict(name=row[0],
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

	return render_template('browse.html', add_events=all_events)
<<<<<<< HEAD
=======

>>>>>>> 18b22e6522cdf773a951920bdde4c1ce733d3fb8
