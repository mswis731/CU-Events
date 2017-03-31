from flask import Flask, render_template, flash, request, redirect, session, url_for
from app.forms import CreateEventForm, SignupForm, SigninForm
from app import app, mysql
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash

@app.route('/')
@app.route('/index')
def index():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	return render_template('index.html', session=session, categories=categories, event_types=event_types)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
	form = SigninForm(request.form)

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', session=session, form = form)
		else:
			session['username'] = form.my_username.data
			return redirect(url_for('profile'))

	elif request.method == 'GET':
		return render_template('signin.html', session=session, form = form)

@app.route('/signup', methods = ['GET', 'POST'])
def sign_up():
	connection = mysql.get_db()
	cursor = connection.cursor()

	form = SignupForm(request.form)
	if request.method == "POST":
		if form.validate() == False:
			flash('Fill in required fields')
			return render_template('signup.html', session=session, form=form)
		else:
			password_hash = generate_password_hash(form.password.data)
			attr = (form.firstname.data, form.lastname.data, form.email.data, form.username.data, password_hash)
			cursor.callproc('CreateUser', (attr[0], attr[1], attr[2], attr[3], attr[4]))
			connection.commit()

			session['username'] = form.username.data
			return redirect(url_for('profile'))

			return("thank you for signing up!")
	elif request.method == 'GET':
		return render_template('signup.html', session=session, form=form)

@app.route('/signout')
def signout():
	if not session['username']:
		return redirect(url_for('signin'))
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/profile')
def profile():
	if not session['username']:
		return redirect(url_for('signin'))

	connection = mysql.get_db()
	cursor = connection.cursor() 

	user = cursor.execute("SELECT * From User Where email = '{}'".format(session['username']))
	if user is None:
		return redirect(url_for('signin'))
	else:
		return render_template('profile.html', session=session)

@app.route('/eventcreate', methods=['GET','POST'])
def event_create():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	# get uid
	if not session.get('username'):
		return redirect("/signup")
	cursor.execute("SELECT uid FROM User WHERE username='{}'".format(session['username']))
	uid = cursor.fetchall()[0][0]

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

		startTime = "{}:{}".format(data[8].seconds//3600, (data[8].seconds//60)%60)
		endTime = "{}:{}".format(data[10].seconds//3600, (data[10].seconds//60)%60)
		form.startDate.data = "{}/{}/{} {}".format(data[7].month, data[7].day, data[7].year, datetime.strptime(startTime, "%H:%M").strftime("%I:%M %p"))
		form.endDate.data = "{}/{}/{} {}".format(data[9].month, data[9].day, data[9].year, datetime.strptime(endTime, "%H:%M").strftime("%I:%M %p"))

		cursor.execute("SELECT categoryName FROM HasCategory WHERE eid={}".format(eid))
		form.categories.data = [ tup[0] for tup in cursor.fetchall() ]
		cursor.execute("SELECT eventType FROM HasEventType WHERE eid={}".format(eid))
		form.eventTypes.data = [ tup[0] for tup in cursor.fetchall() ]

		cursor.execute("SELECT categoryName FROM HasCategory WHERE eid={}".format(eid))
		form.categories.data = [ tup[0] for tup in cursor.fetchall() ]
		cursor.execute("SELECT eventType FROM HasEventType WHERE eid={}".format(eid))
		form.eventTypes.data = [ tup[0] for tup in cursor.fetchall() ]

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
			# only need uid for new events
			if form.eid.data == -1:
				attr_list.append(uid)
			attr = tuple(attr_list)
			# new event
			if form.eid.data == -1:
				cursor.callproc('CreateUserEvent', attr)
			# update event
			else:
				cursor.callproc('UpdateEvent', attr)
				
			connection.commit()

			return redirect('/browse')

	return render_template('eventcreate.html', session=session, form = form, error=error, categories=categories, event_types=event_types)

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
	return render_template('events.html', session=session, categories=categories, event_types=event_types, events=events)

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

	return render_template('events.html', session=session, categories=categories, event_types=event_types, events=events)

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

	return render_template('events.html', session=session, categories=categories, event_types=event_types, events=events)
	
@app.route('/communities')
def communities():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	return render_template('communities.html', session=session, categories=categories, event_types=event_types)

@app.route('/browse/eventid/<id>', methods=['GET','POST'])
def get_event(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT * FROM Event WHERE eid='{}'".format(id))
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
	cursor.close()
	print(len(events))
	print(events[0])
	return render_template('event.html', event = events, session=session)

@app.route('/interested')
def is_interested():
	connection = mysql.get_db()
	cursor = connection.cursor()
	if not session.get('username'):
		return redirect(url_for('signin'))
	else:
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		uid = cursor.fetchall()[0][0]
		curr_url = request.referrer
		curr = curr_url.split('/')[-1]
		cursor.execute("INSERT INTO IsInterestedIn(uid, eid) VALUES({}, {})".format(uid, curr))
		return render_template("profile.html", session=session, curr=curr, uid=uid)