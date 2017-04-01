from flask import Flask, render_template, flash, request, redirect, session, url_for
from wtforms import Form, TextField, TextAreaField, validators, SelectMultipleField, SubmitField, PasswordField, IntegerField, DecimalField
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

class CreateEventForm(Form):
	eid = IntegerField(id = 'eid', validators=[validators.required()])
	title = TextField(id='title', validators=[validators.required()])
	description = TextAreaField('description')
	building = TextField(id = 'building', validators=[validators.required()])
	addrAndStreet = TextField(id ='addrAndStreet', validators=[validators.required()])
	state = TextField(id = 'state', validators=[validators.required()])
	city = TextField(id = 'city', validators=[validators.required()])
	zipcode = IntegerField(id = 'zipcode', validators=[validators.required()])
	startDate = TextField(id = 'startDate', validators=[validators.required()])
	endDate = TextField(id = 'endDate', validators=[validators.required()])
	lowPrice = DecimalField(id = 'lowPrice', places=2, validators=[validators.required()])
	highPrice = DecimalField(id = 'highPrice', places=2, validators=[validators.required()])
	categories = SelectMultipleField(id ='category', choices = ['Academic', 'Arts and Theatre', 'Family', 'Government', 'Health and Wellness', 'Holiday', 'Home and Lifestyle', 'Music', 'Other', 'Outdoors', 'Sports', 'Technology', 'University'])
	eventTypes = SelectMultipleField(id ='eventtype', choices = ['Charity', 'Concerts', 'Conferences', 'Networking and Career Fairs', 'Galleries and Exhibits', 'Other', 'Talks'])

	def dict(self):
		dict = { 'eid' : self.eid.data,
				 'title' : self.title.data,
				 'description': self.description.data,
				 'building': self.building.data,
				 'addrAndStreet': self.addrAndStreet.data,
				 'city': self.city.data,
				 'zipcode': self.zipcode.data,
				 'startDate': self.startDate.data,
				 'endDate': self.endDate.data,
				 'lowPrice': self.lowPrice.data,
				 'highPrice': self.highPrice.data,
				 'categories': self.categories.data,
				 'eventTypes': self.eventTypes.data
		}
		return dict

	def convert_datetime(self, dt):
		d_list = dt.split(' ')[0].split('/')
		t_list = dt.split(' ')[1].split(':')
		am_pm = dt.split(' ')[2].lower()
		if am_pm == 'am':
			if t_list[0] == '12':
				t_list[0] = '00'
		else:
			if t_list[0] != '12':
				t_list[0] = str(int(t_list[0]) + 12)
		
		date = "{}-{}-{}".format(d_list[2], d_list[0], d_list[1])
		time = "{}:{}:00".format(t_list[0], t_list[1])
		return (date,time)
			
	def event_dict(self):
		start_date, start_time = self.convert_datetime(self.startDate.data) 
		end_date, end_time = self.convert_datetime(self.endDate.data) 
		categories = ','.join(map(str, self.categories.data)) 
		eventTypes = ','.join(map(str, self.eventTypes.data)) 

		if self.eid.data:
			dict = { 'eid' : self.eid.data,
				 	'title' : self.title.data,
				 	'description': self.description.data,
				 	'building': self.building.data,
				 	'addrAndStreet': self.addrAndStreet.data,
				 	'city': self.city.data,
				 	'zipcode': self.zipcode.data,
				 	'startDate': start_date,
				 	'startTime': start_time,
				 	'endDate': end_date,
				 	'endTime': end_time,
				 	'lowPrice': self.lowPrice.data,
				 	'highPrice': self.highPrice.data,
				 	'categories': categories,
				 	'eventTypes': eventTypes
			   	   }
		else:
			dict = { 'title' : self.title.data,
				 	'description': self.description.data,
				 	'building': self.building.data,
				 	'addrAndStreet': self.addrAndStreet.data,
				 	'city': self.city.data,
				 	'zipcode': self.zipcode.data,
				 	'startDate': start_date,
				 	'startTime': start_time,
				 	'endDate': end_date,
				 	'endTime': end_time,
				 	'lowPrice': self.lowPrice.data,
					'highPrice': self.highPrice.data,
				 	'categories': categories,
				 	'eventTypes': eventTypes
			   	   }
			
		return dict

class signupForm(Form):
	firstname = TextField("First name") #, [validators.Required(), validators.Length(min = 2, max = 25)])#"Please enter your first name.")])
	lastname = TextField("Last name") #, [validators.Required()])#"Please enter your last name.")])
	username = TextField("username") #, [validators.Required()])#"Please enter a username.")])
	password = PasswordField('Password') #, [validators.Required()])#"Please enter a password.")])
	email = TextField('email')
	submit = SubmitField("Create account") 

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False
		return True

		# user = ("SELECT username FROM User WHERE username = self.username.data LIMIT 1")

		# if user:
		# 	self.username.errors.append("That username is already taken")
		# 	return False
		# else:
			# return True

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

	form.categories.data = []
	form.eventTypes.data = []

	eid = request.args.get('eid')
	if eid:
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

	if request.method == 'POST':
		for key,val in form.dict().items():
			if key != 'categories' and key != 'eventTypes':
				getattr(form, key).data = request.form.get(key)
			else:
				getattr(form, key).data = request.form.getlist(key)

		#TODO: add more validation for form
		if form.title.data != "" and form.startDate.data != "" and form.endDate.data != "" and form.lowPrice.data and form.highPrice.data:
			form_dict = form.event_dict()
			attr = tuple([ form_dict[key] for key in form_dict ])
			# new event
			if not form.eid.data:
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

class CreateCommunityForm(Form):
	name = TextField(id='name', label = 'Group Name', validators=[validators.required("Please enter your group name")])
	
	#categories = SelectMultipleField(id ='category', choices = ['Academic', 'Arts and Theatre', 'Family', 'Government', 'Health and Wellness', 'Holiday', 'Home and Lifestyle', 'Music', 'Other', 'Outdoors', 'Sports', 'Technology', 'University'])
	categories = SelectMultipleField(id ='categories', label='Categories', validators=[validators.Required("Select at least one category for your group")])
	submit = SubmitField("Create Group")

	#def __init__(self, *args, **kwargs):
        # 	Form.__init__(self, *args, **kwargs)

	def __init__(self, form):
		Form.__init__(self, form)

		self.connection = mysql.get_db()
		self.cursor = self.connection.cursor()

		# set category choices
		self.cursor.execute("SELECT name FROM Category")
		categories = [row[0] for row in self.cursor.fetchall()]
		self.categories.choices = [ (c, c) for c in categories ]

	def validate(self):
		if not Form.validate(self):
			return False

		connection = mysql.get_db()
		cursor = connection.cursor() 
		print(self.name.data)
		name = cursor.execute("SELECT name FROM Community Where name = '{}' ".format(self.name.data))
		#print(name)
		if name:
			self.name.errors.append("This group name has already been created!")
			return False
		else:
			return True

@app.route('/communities')
def communities():
	connection = mysql.get_db()
	cursor = connection.cursor()
	#cursor.execute("SELECT name FROM EventType")
	#event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	cursor.execute("SELECT cid, name FROM Community")
	communities = [dict(cid=row[0],
                   name=row[1]) for row in cursor.fetchall()]
	cursor.close()

	return render_template('communities.html', categories=categories)

@app.route('/communitycreate', methods=['GET','POST'])
def create_community():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	print(categories)

	if not session.get('username'):
		uid = '12345'
		#return redirect("/signup")
	else:
		cursor.execute("SELECT uid FROM User WHERE username='{}'".format(session['username']))
		uid = cursor.fetchall()[0][0]
	
	form = CreateCommunityForm(request.form)
	
	if request.method == "POST":
		if form.validate() == False:
			flash('Fill in required fields')
			return render_template('community_create.html', session=session, form=form, categories=categories)
		else:
      # return (form.password.data)
      			#attr = (form.name, form.categories)
			print(form.categories)
			print(form.categories.data)
			#cursor.execute("SELECT name FROM Category")
			#form.categories.data = [ tup[0] for tup in cursor.fetchall() ]
			print(form.name.data)
			print(uid)
			s = ","
			form.categories.data = s.join(form.categories.data)
			print(form.categories.data)
			#category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
			cursor.callproc('CreateCommunity', (form.name.data, uid, form.categories.data))
			connection.commit()
			#return redirect('/browse')
			return("You have successfully created a group! Thank you!")
 
	elif request.method == 'GET':
    		return render_template('community_create.html', session=session, form=form, categories=categories)


