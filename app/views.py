from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, TextAreaField, validators, SelectField
from app import app, mysql
from app.crawlers.eventful import crawl as eventful_crawl
import sys

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

class ReusableForm(Form):
      id = TextField(id = 'id', validators=[validators.required()])
      title = TextField(id='title', validators=[validators.required()])
      description = TextAreaField('description')
      building = TextField(id = 'building', validators=[validators.required()])
      addrAndStreet = TextField(id ='addrAndStreet', validators=[validators.required()])
      state = TextField(id = 'state', validators=[validators.required()])
      city = TextField(id = 'city', validators=[validators.required()])
      zipcode = TextField(id = 'zipcode', validators=[validators.required()])
      startDate = TextField(id = 'startDate', validators=[validators.required()])
      startTime = TextField(id = 'startTime', validators=[validators.required()])
      endDate = TextField(id = 'endDate', validators=[validators.required()])
      endTime = TextField(id = 'endTime', validators=[validators.required()])
      lowPrice = TextField(id = 'lowPrice', validators=[validators.required()])
      highPrice = TextField(id = 'highPrice', validators=[validators.required()])
      category = SelectField(id ='category', choices = ['Academic', 'Arts and Theatre', 'Family', 'Government', 'Health and Wellness', 'Holiday', 'Home and Lifestyle', 'Music', 'Other', 'Outdoors', 'Sports', 'Technology', 'University'])
      eventtype = SelectField(id ='eventtype', choices = ['Charity', 'Concerts', 'Conferences', 'Networking and Career Fairs', 'Galleries and Exhibits', 'Other', 'Talks'])

@app.route('/eventcreate', methods=['GET','POST'])
def signup():
	connection = mysql.get_db()
	cursor = connection.cursor()
	form = ReusableForm(request.form)
	error = None
	eventID = request.args.get('id')
	print(eventID)
	prefill ={"id":"-1", "title":"", "description":"", "building":"", "addrAndStreet":"", "city":"", "zipcode":"", "startDate":"", "startTime":"", "endDate":"", "endTime":"", "lowPrice":"", "highPrice":""}
	if eventID:
		cursor.execute("SELECT * FROM Event WHERE id={}".format(eventID))
		data = cursor.fetchall()[0]
		index = 0
		for key in prefill:
			prefill[key]=data[index] if data[index] else ""
			index+=1

	if request.method == 'POST':
		eventID = request.form['id']
		title =  request.form['title'] if request.form['title'] != "" else None
		description = request.form['description']
		building = request.form['building']
		addrAndStreet= request.form['addrAndStreet']
		city = request.form['city']
		zipcode = request.form['zipcode']
		startDate = request.form['startDate']
		startTime = request.form['startTime']
		endDate = request.form['endDate']
		endTime = request.form['endTime']
		lowPrice = request.form['lowPrice']
		highPrice = request.form['highPrice']
		category = request.form['category']
		eventType = request.form['eventtype']


		print(eventID)
		print("reached")
		#try:
		cursor.callproc('CreateUserEvent', (eventID,
												title,
            								    description,
            									building,
            									addrAndStreet,
            									city,
            									zipcode,
            									startDate,
            									startTime,
            									endDate,
            									endTime,
            									lowPrice,
            									highPrice,
            									category,
            									eventType))

		connection.commit()

		return redirect('/browse/category/{}'.format(category))




	"""
    if form.validate():
    	error = 'Thanks for registering the event' 
    else:
    	error = 'Error: Missing Filling a form field'
    """

	return render_template('eventcreate.html', prefill=prefill, form = form, error=error)

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

@app.route('/browse/category/<category>', methods=['GET','POST'])
def event_(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	
	if request.method == 'POST':
		btn_id = request.form['btn']
		# delete button was pressed
		if btn_id[0] == 'd':
			event_id = btn_id[1:]
			cursor.execute("DELETE FROM Event WHERE id={}".format(event_id))
			connection.commit()
			return redirect("/browse/category/{}".format(category))
		# edit button was pressed
		else:
			return redirect("/eventcreate")

	category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
	cursor.execute("SELECT * FROM Event WHERE (id) IN (SELECT eventID FROM HasCategory WHERE categoryName='{}')".format(category))
	events = [dict(id=row[0],
				   title=row[1],
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
	
	if request.method == 'POST':
		btn_id = request.form['btn']
		# delete button was pressed
		if btn_id[0] == 'd':
			event_id = btn_id[1:]
			cursor.execute("DELETE FROM Event WHERE id={}".format(event_id))
			connection.commit()
			return redirect("/browse/category/{}".format(category))
		# edit button was pressed
		else:
			return redirect("/eventcreate")

	e_type = " ".join([ (word.capitalize() if word != 'and' else word) for word in e_type.split('-') ])
	cursor.execute("SELECT * FROM Event WHERE (id) IN (SELECT eventID FROM HasEventType WHERE eventType='{}')".format(e_type))
	events = [dict(id=row[0],
				   title=row[1],
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
