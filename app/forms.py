from app import mysql
from wtforms import Form, TextField, TextAreaField, validators, SelectMultipleField, SubmitField, PasswordField, IntegerField, DecimalField
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash

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

		res_len = cursor.execute("SELECT password FROM User WHERE username = '{}'" .format(self.my_username.data))
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


# HEAD
class CreateCommunityForm(Form):
	name = TextField(id='name', label = 'Community Name', validators=[validators.required("Please enter your group name")])
	
	#categories = SelectMultipleField(id ='category', choices = ['Academic', 'Arts and Theatre', 'Family', 'Government', 'Health and Wellness', 'Holiday', 'Home and Lifestyle', 'Music', 'Other', 'Outdoors', 'Sports', 'Technology', 'University'])
	categories = SelectMultipleField(id ='categories', label='Categories', validators=[validators.Required("Select at least one category for your community")])
	submit = SubmitField("Create Community")

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
		#print(self.name.data)
		print(self.name.data.replace('\'', '/'))
		#print(self.name.data)
		result_length = cursor.execute("SELECT name FROM Community Where name = '{}' ".format(self.name.data.replace('\'', '/')))
		#print(name)
		if result_length:
			self.name.errors.append("This group name has already been created!")
			return False
		else:
			return True
