from flask import Flask, render_template, flash, request, redirect, session, url_for
from app.forms import *

from app.filters import *

from app import app, mysql
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from flask_paginate import Pagination
import googlemaps

def cat_and_types(connection, cursor):
	cursor.execute("SELECT name FROM EventType")
	event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	return (event_types, categories)

@app.route('/')
@app.route('/index')
def index():
	connection = mysql.get_db()
	cursor = connection.cursor()
	

	event_types, categories = cat_and_types(connection, cursor)
	return render_template('index.html', categories=categories, event_types=event_types)



@app.route('/signin', methods = ['GET', 'POST'])
def signin():
	form = SigninForm(request.form)

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('signin.html', session=session, form = form)
# origin/master
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

	cursor.execute("SELECT Event.eid, title, startDate, building, lowPrice, highPrice FROM IsInterestedIn, User, Event WHERE IsInterestedIn.uid = User.uid AND User.username = '{}' AND Event.eid = IsInterestedIn.eid".format(session['username']))
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()]

	user = cursor.execute("SELECT * From User Where username = '{}'".format(session['username']))
	if user is None:
		return redirect(url_for('signin'))
	else:
		return render_template('profile.html', session=session, events = events)

@app.route('/eventcreate', methods=['GET','POST'])
def event_create():
	connection = mysql.get_db()
	cursor = connection.cursor()
	event_types, categories = cat_and_types(connection, cursor)

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
				elif field.name == 'categories' or field.name == 'eventTypes':
					attr_list.append(','.join(map(str, field.data)))
				else:
					attr_list.append(field.data)
			# only need uid for new events
			if form.eid.data == -1:
				attr_list.append(uid)
			attr = tuple(attr_list)
			print(attr)
			# new event
			if form.eid.data == -1:
				cursor.callproc('CreateUserEvent', attr)
			# update event
			else:
				cursor.callproc('UpdateEvent', attr)
				
			connection.commit()

			return redirect('/browse')

	return render_template('eventcreate.html', session=session, form = form, error=error, categories=categories, event_types=event_types)



MAX_PER_PAGE = 20

@app.route('/browse/', methods=['GET', 'POST'])
def browse():
	connection = mysql.get_db()
	cursor = connection.cursor()
	event_types, categories = cat_and_types(connection, cursor)

	page = request.args.get('page', type=int, default=1)
	res_len = cursor.execute("SELECT eid, title, startDate, building, lowPrice, highPrice FROM Event")
	start_row = MAX_PER_PAGE*(page-1)
	end_row = start_row+MAX_PER_PAGE if (start_row+MAX_PER_PAGE < res_len) else res_len
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()[start_row:end_row]]
	cursor.close()

	pagination = Pagination(page=page, total=res_len, per_page=MAX_PER_PAGE, css_framework='bootstrap3')
	return render_template('events.html', session=session, categories=categories, event_types=event_types, events=events, pagination=pagination)

@app.route('/browse/category/<category>', methods=['GET','POST'])
def event_(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	event_types, categories = cat_and_types(connection, cursor)

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

	page = request.args.get('page', type=int, default=1)
	category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
	res_len = cursor.execute("SELECT eid, title, startDate, building, lowPrice, highPrice FROM Event WHERE (eid) IN (SELECT eid FROM HasCategory WHERE categoryName='{}')".format(category))
	start_row = MAX_PER_PAGE*(page-1)
	end_row = start_row+MAX_PER_PAGE if (start_row+MAX_PER_PAGE < res_len) else res_len
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()[start_row:end_row]]
	cursor.close()

	pagination = Pagination(page=page, total=res_len, per_page=MAX_PER_PAGE, css_framework='bootstrap3')
	return render_template('events.html', session=session, categories=categories, event_types=event_types, events=events, pagination=pagination)

@app.route('/browse/type/<e_type>', methods=['GET','POST'])
def event_type(e_type):
	connection = mysql.get_db()
	cursor = connection.cursor()
	event_types, categories = cat_and_types(connection, cursor)

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

	page = request.args.get('page', type=int, default=1)
	e_type = " ".join([ (word.capitalize() if word != 'and' else word) for word in e_type.split('-') ])
	res_len = cursor.execute("SELECT eid, title, startDate, building, lowPrice, highPrice FROM Event WHERE (eid) IN (SELECT eid FROM HasEventType WHERE eventType='{}')".format(e_type))
	start_row = MAX_PER_PAGE*(page-1)
	end_row = start_row+MAX_PER_PAGE if (start_row+MAX_PER_PAGE < res_len) else res_len
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()[start_row:end_row]]
	cursor.close()

	pagination = Pagination(page=page, total=res_len, per_page=MAX_PER_PAGE, css_framework='bootstrap3')
	return render_template('events.html', session=session, categories=categories, event_types=event_types, events=events, pagination=pagination)
	

@app.route('/browse/eventid/<id>', methods=['GET','POST'])
def get_event(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	event_types, categories = cat_and_types(connection, cursor)
	
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



@app.route('/communities')
def communities():
	connection = mysql.get_db()
	cursor = connection.cursor()
	#cursor.execute("SELECT name FROM EventType")
	#event_types = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	#cursor.execute("SELECT name FROM Category")
	#categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	event_types, categories = cat_and_types(connection, cursor)

	cursor.execute("SELECT cid, name, uid FROM Community")
	communities = [dict(cid=row[0],
                   name=row[1].replace('/', '\''), uid=row[2]) for row in cursor.fetchall()]
	cursor.close()

	return render_template('communities.html', categories=categories, communities=communities)

@app.route('/communitycreate', methods=['GET','POST'])
def create_community():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]
	print(categories)

	if not session.get('username'):
		#uid = '12345'
		return redirect("/signup")
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
			#print(form.categories)
			#print(form.categories.data)
			#cursor.execute("SELECT name FROM Category")
			#form.categories.data = [ tup[0] for tup in cursor.fetchall() ]
			#print(form.name.data)
			#print(uid)
			s = ","
			form.categories.data = s.join(map(str, form.categories.data))
			
			#print(form.categories.data)
			#category = " ".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
			cursor.callproc('CreateCommunity', (form.name.data.replace('\'', '/'), uid, form.categories.data))
			#cursor.execute("INSERT INTO IsCommunityMember(uid, cid) VALUES({}, {})".format(uid, cid)
			cursor.execute("SELECT cid FROM Community WHERE name='{}'".format(form.name.data.replace('\'', '/')))
			cid = cursor.fetchall()[0][0]
			print(cid)
			print(uid)
			cursor.execute("INSERT INTO IsCommunityMember(uid, cid) VALUES({}, {})".format(uid, cid))
			cursor.close()
			connection.commit()
			#return redirect('/browse')
			return redirect(url_for('communities'))
 
	elif request.method == 'GET':
    		return render_template('community_create.html', session=session, form=form, categories=categories)

@app.route('/communities/category/<category>', methods=['GET','POST'])
def community_(category):
	connection = mysql.get_db()
	cursor = connection.cursor()
	event_types, categories = cat_and_types(connection, cursor)


	page = request.args.get('page', type=int, default=1)
	category = ",".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
	print(category)
	res_len = cursor.execute("SELECT cid, name, uid FROM Community WHERE (cid) IN (SELECT cid FROM CommunityCategories WHERE categoryName='{}')".format(category))
	start_row = MAX_PER_PAGE*(page-1)
	print(start_row)
	end_row = start_row+MAX_PER_PAGE if (start_row+MAX_PER_PAGE < res_len) else res_len
	print(end_row)
	communities = [dict(cid=row[0],
                   name=row[1].replace('/', '\''), uid=row[2]) for row in cursor.fetchall()[start_row:end_row]]
	cursor.close()

	pagination = Pagination(page=page, total=res_len, per_page=MAX_PER_PAGE, css_framework='bootstrap3')
	return render_template('communities.html', session=session, categories=categories, event_types=event_types, communities=communities, pagination=pagination)

#
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
		connection.commit()
		return render_template("profile.html", session=session, curr=curr, uid=uid)

# origin/master

@app.context_processor
def googlelocfilter():
	def _googlelocfilter(building, addr, city, cityzip):
		
		locstr = addr+","+city+", IL," + str(cityzip)
		gmaps = googlemaps.Client(key='AIzaSyCwQgKvuUKzqEkWbNs8VjlHHMkDYri7bKs')
		ret = gmaps.geocode(address=locstr)
		lng = ret[0]['geometry']['location']['lng']
		lat = ret[0]['geometry']['location']['lat']
		cordstr = str(lng)+","+str(lat)
		addrmod = addr.replace(" ", "+")
		buildingmod = building.replace(" ", "+")
		locstr2 = buildingmod+"+"+addrmod
		locstr3 = locstr2+",+"+str(cityzip)+",+USA"
		mapstr =  "https://maps.google.co.uk/maps?f=q&source=s_q&hl=en&geocode=&q="+locstr2+"&sll="+cordstr+"&ie=UTF8&hq=&hnear="+locstr3+"&t=m&z=17"+"&ll="+cordstr+"&output=embed"
		return mapstr
	return dict(googlelocfilter=_googlelocfilter)


@app.route('/communities/communityid/<id>', methods=['GET','POST'])
def community(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	#event_types, categories = cat_and_types(connection, cursor)
	

	cursor.execute("SELECT name, uid FROM Community WHERE cid='{}'".format(id))
	#print(cursor.fetchall())
	#print(cursor.fetchall()[0])
	info_tuple = cursor.fetchall()[0]
	cname = info_tuple[0]
	uid = info_tuple[1]
	print(cname)
	print(uid)
	
	cursor.execute("SELECT categoryName FROM CommunityCategories WHERE cid='{}'".format(id))
	categories_list = cursor.fetchall()
	community_categories = ""
	for row in categories_list:
		community_categories += row[0]
		community_categories += ","
	community_categories = community_categories[:-1]
	print("this is the category")
	print(community_categories)	

	cursor.execute("SELECT username FROM User WHERE uid ='{}'".format(uid))
	username = cursor.fetchall()[0][0]
	print(username)

	#cursor.execute("SELECT uid FROM isCommunityMember WHERE cid ='{}'".format(id))
	#uid_list = cursor.fetchall()
	#print(uid_list)

	cursor.execute("SELECT username FROM User WHERE uid IN (SELECT uid FROM isCommunityMember WHERE cid ='{}')".format(id))
	member_list = cursor.fetchall()
	print(member_list)
	#I was gonna print out all the community members but didn't succeed
	
	cursor.close()
	return render_template("community.html", cid=id, cname=cname, community_categories=community_categories, username=username, session=session)



@app.route('/communities/communityid/<id>/joined')
def is_communitymember(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	if not session.get('username'):
		return redirect(url_for('signin'))
	else:
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		uid = cursor.fetchall()[0][0]
		#cid = id
		cursor.execute("INSERT INTO IsCommunityMember(uid, cid) VALUES({}, {})".format(uid, id))

		cursor.execute("SELECT name, uid FROM Community WHERE cid='{}'".format(id))
		#print(cursor.fetchall())
		#print(cursor.fetchall()[0])
		info_tuple = cursor.fetchall()[0]
		cname = info_tuple[0]
		uid = info_tuple[1]
		print(cname)
		print(uid)
	
		cursor.execute("SELECT categoryName FROM CommunityCategories WHERE cid='{}'".format(id))
		categories_list = cursor.fetchall()
		community_categories = ""
		for row in categories_list:
			community_categories += row[0]
			community_categories += ","
		community_categories = community_categories[:-1]
		print("this is the category")
		print(community_categories)	

		cursor.execute("SELECT username FROM User WHERE uid ='{}'".format(uid))
		username = cursor.fetchall()[0][0]
		print(username)

	#cursor.execute("SELECT uid FROM isCommunityMember WHERE cid ='{}'".format(id))
	#uid_list = cursor.fetchall()
	#print(uid_list)

		cursor.execute("SELECT username FROM User WHERE uid IN (SELECT uid FROM isCommunityMember WHERE cid ='{}')".format(id))
		member_list = cursor.fetchall()
		print(member_list)
		connection.commit()
		return render_template("community_joined.html", cid=id, cname=cname, community_categories=community_categories, username=username, session=session)


@app.route('/communities/communityid/<id>/unjoined')
def is_not_communitymember(id):
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
	uid = cursor.fetchall()[0][0]
	#cid = id
	cursor.execute("DELETE FROM isCommunityMember WHERE uid = '{}' AND cid = '{}'".format(uid, id))
	connection.commit()
	return redirect(url_for('community', id=id))
	
