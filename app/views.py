from flask import Flask, render_template, flash, request, redirect, session, url_for
from app.forms import CreateEventForm, signupForm
from app import app, mysql
from app.crawlers.eventful import crawl as eventful_crawl
import sys

@app.route('/')
@app.route('/index')
def index():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	return render_template('index.html', categories=categories, event_types=event_types)

@app.route('/signUp', methods = ['GET', 'POST'])
def sign_up():
	connection = mysql.get_db()
	cursor = connection.cursor()

	form = signupForm(request.form)
	if request.method == "POST":
		if form.validate() == False:
			flash('Fill in required fields')
			return render_template('signUp.html', form=form)
		else:
			# return (form.password.data)
			 attr = (form.firstname.data, form.lastname.data, form.email.data, form.username.data, form.password.data)
			 cursor.callproc('CreateUser', (attr[0], attr[1], attr[2], attr[3], attr[4]))
			 connection.commit()
			 return("thank you for signing up!")

	elif request.method == 'GET':
		return render_template('signup.html', form=form)

@app.route('/eventcreate', methods=['GET','POST'])
def event_create():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	form = CreateEventForm(request.form)
	error = None

	eid = request.args.get('eid')
	if request.method == "GET" and eid:
		cursor.execute("SELECT * FROM Event WHERE eid={}".format(eid))
		data = cursor.fetchall()[0]
		form.eid.data = data[0]
		form.title.data = data[1]
		form.description.data = data[2]
		form.building.data = data[3]
		form.addrAndStreet.data = data[4]
		form.city.data = data[5]
		form.zipcode.data = data[6]
		form.lowPrice.data = data[11]
		form.highPrice.data = data[12]

		start_hours = data[8].seconds//3600
		start_minutes = (data[8].seconds//60)%60
		start_am_pm = ""
		if start_hours >= 12:
			start_am_pm = "PM"
			if start_hours > 12:
				start_hours -= 12
		else:
			if start_hours == 0:
				start_hours = 12
			start_am_pm = "AM"
		end_hours = data[10].seconds//3600
		end_minutes = (data[10].seconds//60)%60
		end_am_pm = ""
		if end_hours >= 12:
			end_am_pm = "PM"
			if end_hours > 12:
				end_hours -= 12
		else:
			if end_hours == 0:
				end_hours = 12
			end_am_pm = "AM"
		form.startDate.data = "{}/{}/{} {}:{} {}".format(data[7].month, data[7].day, data[7].year, start_hours, start_minutes, start_am_pm)
		form.endDate.data = "{}/{}/{} {}:{} {}".format(data[9].month, data[9].day, data[9].year, end_hours, end_minutes, end_am_pm)

		cursor.execute("SELECT categoryName FROM HasCategory WHERE eid={}".format(eid))
		form.categories.data = [ tup[0] for tup in cursor.fetchall() ]
		cursor.execute("SELECT eventType FROM HasEventType WHERE eid={}".format(eid))
		form.eventTypes.data = [ tup[0] for tup in cursor.fetchall() ]

		cursor.execute("SELECT categoryName FROM HasCategory WHERE eid={}".format(eid))
		form.categories.data = [ tup[0] for tup in cursor.fetchall() ]
		cursor.execute("SELECT eventType FROM HasEventType WHERE eid={}".format(eid))
		form.eventTypes.data = [ tup[0] for tup in cursor.fetchall() ]

		form.submit.value = "Update Event"

	if request.method == 'POST':
		if form.validate():
			attr_list = []
			for field in form:
				if (field.name == 'eid' and field.data == -1) or field.name=='submit':
					continue
				if field.name == 'startDate':
					attr_list.append(form.start[0])
					attr_list.append(form.start[1])
				elif field.name == 'endDate':
					attr_list.append(form.end[0])
					attr_list.append(form.end[1])
				else:
					attr_list.append(field.data)
			attr = tuple(attr_list)
			# new event
			if form.eid.data == -1:
				cursor.callproc('CreateUserEvent', attr)
			# update event
			else:
				cursor.callproc('UpdateEvent', attr)
				
			connection.commit()

			return redirect('/browse')

	return render_template('eventcreate.html', form = form, error=error, categories=categories, event_types=event_types)

# filters needed for listing events
@app.template_filter('month')
def year_filter(num):
	abbrs = { 1 : "Jan",
			  2 : "Feb",	
			  3 : "Mar",	
			  4 : "Apr",	
			  5 : "May",	
			  6 : "Jun",	
			  7 : "Jul",	
			  8 : "Aug",	
			  9 : "Sep",	
			  10 : "Oct",	
			  11 : "Nov",	
			  12 : "Dec" }
	abbr = abbrs[num] if abbrs.get(num) else ""
	return abbr

@app.template_filter('money')
def money_filter(val):
	return "${:,.2f}".format(val)

@app.route('/browse')
def browse():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	cursor.execute("SELECT eid, title, startDate, building, lowPrice, highPrice FROM Event")
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()]
	cursor.close()
	return render_template('events.html', categories=categories, event_types=event_types, events=events)

@app.route('/browse/category/<category>', methods=['GET','POST'])
def event_(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	"""
	if request.method == 'POST':
		btn_id = request.form['btn']
		# delete button was pressed
		if btn_id[0] == 'd':
			event_id = btn_id[1:]
			cursor.execute("DELETE FROM Event WHERE eid={}".format(event_id))
			connection.commit()
			return redirect("/browse/category/{}".format(category))
		# edit button was pressed
		else:
			return redirect("/eventcreate")
	"""

	category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
	cursor.execute("SELECT eid, title, startDate, building, lowPrice, highPrice FROM Event WHERE (eid) IN (SELECT eid FROM HasCategory WHERE categoryName='{}')".format(category))
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()]
	cursor.close()

	return render_template('events.html', categories=categories, event_types=event_types, events=events)

@app.route('/browse/type/<e_type>', methods=['GET','POST'])
def event_type(e_type):
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	"""
	if request.method == 'POST':
		btn_id = request.form['btn']
		# delete button was pressed
		if btn_id[0] == 'd':
			event_id = btn_id[1:]
			cursor.execute("DELETE FROM Event WHERE eid={}".format(event_id))
			connection.commit()
			return redirect("/browse/type/{}".format(e_type))
		# edit button was pressed
		else:
			return redirect("/eventcreate")
	"""

	e_type = " ".join([ (word.capitalize() if word != 'and' else word) for word in e_type.split('-') ])

	cursor.execute("SELECT eid, title, startDate, building, lowPrice, highPrice FROM Event WHERE (eid) IN (SELECT eid FROM HasEventType WHERE eventType='{}')".format(e_type))
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()]
	cursor.close()

	return render_template('events.html', categories=categories, event_types=event_types, events=events)
	
@app.route('/communities')
def communities():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	return render_template('communities.html', categories=categories, event_types=event_types)

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

