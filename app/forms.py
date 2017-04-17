from app import mysql, GMAPS_KEY
from wtforms import Form, TextField, TextAreaField, validators, SelectField, SelectMultipleField, SubmitField, PasswordField, IntegerField, DecimalField
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
import googlemaps

class CreateEventForm(Form):
	eid = IntegerField(id = 'eid', default=-1)
	title = TextField(id='title', label='Title', validators=[validators.Required("Title is missing")])
	description = TextAreaField(id='description', label='Description')
	building = TextField(id = 'building', validators=[validators.Required("Building name is missing")])
	addrAndStreet = TextField(id ='addrAndStreet', validators=[validators.Required("Address is missing")])
	city = TextField(id = 'city', default='Champaign', validators=[validators.Required("City is missing")])
	zipcode = TextField(id = 'zipcode', default='61820', validators=[validators.InputRequired("Zipcode is invalid")])
	startDate = TextField(id = 'startDate', label='Start Date', validators=[validators.Required("Start date is missing")])
	endDate = TextField(id = 'endDate', label='End Date', validators=[validators.Required("End date is missing")])
	lowPrice = DecimalField(id = 'lowPrice', places=2, validators=[validators.InputRequired("Lower bound on price range is invalid")])
	highPrice = DecimalField(id = 'highPrice', places=2, validators=[validators.InputRequired("Upper bound on price range is invalid")])
	categories = SelectMultipleField(id ='category', label='Categories', validators=[validators.Required("Select at least one category")])
	eventTypes = SelectMultipleField(id ='eventtype', label='Event Types', validators=[validators.Required("Select at least one event type")])
	submit = SubmitField("Create Event") 

	def __init__(self, form):
		Form.__init__(self, form)

		self.connection = mysql.get_db()
		self.cursor = self.connection.cursor()

		# set category choices
		self.cursor.execute("SELECT name FROM Category")
		categories = [row[0] for row in self.cursor.fetchall()]
		self.categories.choices = [ (c, c) for c in categories ]

		# set event types choices
		self.cursor.execute("SELECT name FROM EventType")
		event_types = [row[0] for row in self.cursor.fetchall()]
		self.eventTypes.choices = [ (e, e) for e in event_types ]

		# startDate, startTime, endDate, endTime in database format
		self.start = ('', '')
		self.end = ('', '')

		#lat and lng
		self.lat = 0,0
		self.lng = 0.0

	def validate(self):
		if not Form.validate(self):
			return False

		valid = True

		# zipcode
		try:
			# check if zipcode is within possible Illinois zipcodes
			if int(self.zipcode.data) < 60001 or int(self.zipcode.data) > 62999:
				self.zipcode.errors.append("Zipcode is invalid")
				valid = False
		except:
			self.zipcode.errors.append("Zipcode is invalid")
			valid = False

		# lowPrice and highPrice
		if self.lowPrice.data < 0 or self.highPrice.data < 0 or self.lowPrice.data > self.highPrice.data:
			self.lowPrice.errors.append("Price range is invalid")
			valid = False

		# startDate and endDate
		parsedDates = True
		try:
			start = datetime.strptime(self.startDate.data, '%m/%d/%Y %I:%M %p')
		except:
			self.startDate.errors.append("Start date is invalid")
			parsedDates = False
			valid = False
		try:
			end = datetime.strptime(self.endDate.data, '%m/%d/%Y %I:%M %p')
		except:
			self.endDate.errors.append("End date is invalid")
			parsedDates = False
			valid = False

		if parsedDates:
			if start >= end or end < datetime.now():
				self.startDate.errors.append("Start and end dates are invalid")
				valid = False
			# valid dates
			else:
				self.start = ("{}-{}-{}".format(start.year, start.month, start.day), "{}:{}:00".format(start.hour, start.minute))
				self.end = ("{}-{}-{}".format(end.year, end.month, end.day), "{}:{}:00".format(end.hour, end.minute))
			
				# check for existing event if creating a new event
				if self.eid.data == -1:
					result_len = self.cursor.execute("SELECT * FROM Event WHERE title='{}' AND startDate='{}' AND startTime='{}'".format(self.title.data, self.start[0], self.start[1]))
					if result_len >= 1:
						self.title.errors.append("An event with similar information already exists")

		# validate address
		locstr = self.addrAndStreet.data+ "," + self.city.data + ", IL," + str(self.zipcode.data)
		gmaps = googlemaps.Client(key=GMAPS_KEY)
		ret = gmaps.geocode(address=locstr)
		if len(ret) == 0:
			valid = False
			self.addrAndStreet.errors.append("Invalid address")
		else:
			# look for minor errors in address
			street_num = ""
			street_name = ""
			city = ""
			zipcode = ""
			for dict in ret[0]['address_components']:
				if 'street_number' in dict['types']:
					street_num = dict['short_name']
				elif 'route' in dict['types']:
					street_name = dict['short_name']
				elif 'locality' in dict['types']:
					city = dict['short_name']
				elif 'postal_code' in dict['types']:
					zipcode = dict['short_name']

			if not (street_num and street_name and city and zipcode):
				valid = False
				self.addrAndStreet.errors.append("Invalid address")
			else:
				self.addrAndStreet.data = street_num + " " + street_name
				self.city.data = city
				self.zipcode.data = zipcode

				self.lat = "{0:.7f}".format(ret[0]['geometry']['location']['lat'])
				self.lng = "{0:.7f}".format(ret[0]['geometry']['location']['lng'])
		
		return valid
		
class SignupForm(Form):
	firstname = TextField("First Name", [validators.Required("Please enter your first name.")])
	lastname = TextField("Last Name", [validators.Required("Please enter your last name")])
	username = TextField("Username", [validators.Required("Please enter a username.")])
	password = PasswordField('Password', [validators.Required("Please enter a password.")])
	confirm_password = PasswordField('Confirm Password', [validators.Required("Please confirm password.")])

	email = TextField('Email')
	submit = SubmitField("Create Account") 

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False

		connection = mysql.get_db()
		cursor = connection.cursor() 

		user = cursor.execute("SELECT username FROM User Where username = '{}' ".format(self.username.data))
		if user:
			self.username.errors.append("That username is already taken")
			return False
		else:
			email = cursor.execute("SELECT email FROM User WHERE email = '{}'" .format(self.email.data))
			if email:
				self.email.errors.append("That email is already associated with an account")
				return False
			else:
				if self.confirm_password.data != self.password.data:
					self.confirm_password.errors.append("Passwords do not match")
					return False
				else:
					return True

class SigninForm(Form):
	my_username = TextField("Username", [validators.Required("Please enter your email address")])
	my_password = PasswordField("Password", [validators.Required("please enter your password")])
	sign_in_submit = SubmitField("Sign In")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if not Form.validate(self):
			return False

		connection = mysql.get_db()
		cursor = connection.cursor()

		res_len = cursor.execute("SELECT password FROM User WHERE username = '{}'".format(self.my_username.data))
		if res_len == 0:
			self.my_username.errors.append("Invalid username")
			return False
		else:
			password = cursor.fetchall()[0][0]
			if check_password_hash(password, self.my_password.data):
				return True
			else:
				self.my_password.errors.append("Invalid password")
				return False

class searchBy(Form):
	searchTerm = TextField(id = 'searchTerm')
	category = SelectField(id ='category', label='Category')
	eventType = SelectField(id ='eventtype', label='Event Type')
	daterange = TextField(id = 'daterange')
	price = SelectField(id='price', label='Price', choices=[('All Prices', 'All Prices'), ('Free', 'Free'), ('Paid', 'Paid')])
	submit = SubmitField("Search") 

	def __init__(self, form):
		Form.__init__(self, form)

		self.connection = mysql.get_db()
		self.cursor = self.connection.cursor()

		# set category choices
		self.cursor.execute("SELECT name FROM Category")
		categories = [row[0] for row in self.cursor.fetchall()]
		categories.insert(0, 'All Categories')
		categories.insert(1, 'User Created')
		self.category.choices = [ (c, c) for c in categories ]

		# set event types choices
		self.cursor.execute("SELECT name FROM EventType")
		event_types = [row[0] for row in self.cursor.fetchall()]
		event_types.insert(0, 'All Event Types')
		self.eventType.choices = [ (e, e) for e in event_types ]
		
	def validate(self):
		return True
	
	# format: MM/DD/YYYY - MM/DD/YYYY
	def get_daterange(self):
		if self.daterange.data:
			try:
				start_orig = self.daterange.data.split('-')[0].strip()
				end_orig = self.daterange.data.split('-')[1].strip()
				s_dt = datetime.strptime(start_orig, '%m/%d/%Y')
				e_dt = datetime.strptime(end_orig, '%m/%d/%Y')

				start = "{}-{}-{}".format(s_dt.year, s_dt.month, s_dt.day)
				end = "{}-{}-{}".format(e_dt.year, e_dt.month, e_dt.day)

				return (start, end)
			except:
				pass

		return (None, None)
	
	# format: YYYY-MM-DD
	def set_daterange(self, start, end):
		try:
			s_dt = datetime.strptime(start, '%Y-%m-%d')
			e_dt = datetime.strptime(end, '%Y-%m-%d')

			self.daterange.data = "{:02d}/{:02d}/{} - {:02d}/{:02d}/{}".format(s_dt.month, s_dt.day, s_dt.year, e_dt.month, e_dt.day, e_dt.year)
		except:
			pass

class interest_form(Form):
	categories = SelectMultipleField(id ='category', label='Categories')
	submit = SubmitField("update")

	def __init__(self, form):
		Form.__init__(self, form)
		self.connection = mysql.get_db()
		self.cursor = self.connection.cursor()

		self.cursor.execute("SELECT name FROM Category")
		categories = [row[0] for row in self.cursor.fetchall()]
		self.categories.choices = [ (c, c) for c in categories ]


	def validate(self):
		return True

class EventsNearMeForm(Form):
	radius = SelectField(id='radius', label='Radius', choices=[(0.5, '0.5 mi'), (1, '1 mi'), (2, '2 mi'), (5, '5 mi') ], default=1, validators=[validators.Required("Radius is missing")])
	limit = SelectField(id='limit', label='Limit', choices=[(10, '10'), (50, '50'), (100, '100')], default=50, validators=[validators.Required("Limit is missing")])
	submit = SubmitField("Filter") 
