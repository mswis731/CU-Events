from flask import Flask, render_template, flash, request, redirect, session, url_for
from wtforms import Form, TextField, TextAreaField, validators, SelectMultipleField, SubmitField, PasswordField, IntegerField, DecimalField
from app import app, mysql
from app.crawlers.eventful import crawl as eventful_crawl
from werkzeug import generate_password_hash, check_password_hash
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

  return render_template('index.html', session=session, categories=categories, event_types=event_types)

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


class SigninForm(Form):
	my_username = TextField("username", [validators.Required("Please enter your email address")])
	my_password = PasswordField("Password", [validators.Required("please enter your password")])
	sign_in_submit = SubmitField("sign in")

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

class signupForm(Form):
  firstname = TextField("First name", [validators.Required("Please enter your first name.")])
  lastname = TextField("Last name", [validators.Required("Please enter your last name")])
  username = TextField("username", [validators.Required("Please enter a username.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  confirm_password = PasswordField('Confirm Password', [validators.Required("Please confirm password.")])

  email = TextField('email')
  categories = SelectMultipleField(id ='category', choices = ['Academic', 'Arts and Theatre', 'Family', 'Government', 'Health and Wellness', 'Holiday', 'Home and Lifestyle', 'Music', 'Other', 'Outdoors', 'Sports', 'Technology', 'University'])

  submit = SubmitField("Create account") 

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

  def validate(self):
    if not Form.validate(self):
      return False

    connection = mysql.get_db()
    cursor = connection.cursor() 

    user = cursor.execute("SELECT username FROM User Where username = '{}' ".format(self.username.data))
    print(user)
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

@app.route('/signup', methods = ['GET', 'POST'])
def sign_up():

  connection = mysql.get_db()
  cursor = connection.cursor()

  form = signupForm(request.form)
  
  cursor.execute("SELECT name FROM Category")
  categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

  if request.method == "POST":
    if form.validate() == False:
      flash('Fill in required fields')
      return render_template('signup.html', session=session, form=form, categories=categories)
    else:
      # return (form.password.data)
      password_hash = generate_password_hash(form.password.data)
      print(password_hash)
      print(len(password_hash))
      attr = (form.firstname.data, form.lastname.data, form.email.data, form.username.data, password_hash)
      cursor.callproc('CreateUser', (attr[0], attr[1], attr[2], attr[3], attr[4]))
      connection.commit()

      session['username'] = form.username.data
      return redirect(url_for('profile'))

      return("thank you for signing up!")
 
  elif request.method == 'GET':
    return render_template('signup.html', session=session, form=form, categories=categories)

@app.route('/signout')
def signout():
  if not session['username']:
    return redirect(url_for('signin'))
  session.pop('username', None)
  return redirect(url_for('index'))

@app.route('/profile')
def profile():
  if 'username' not in session:
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
  events = [dict(id=row[0],
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

