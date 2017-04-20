from flask import Flask, render_template, flash, request, redirect, session, url_for, Response, jsonify
from app.forms import *
from app.filters import *
from app import app, mysql, GMAPS_KEY
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from flask_paginate import Pagination
import googlemaps
import json
from urllib.request import urlopen
from haversine import haversine
from geocoder import ipinfo
import sys

@app.route('/')
@app.route('/index')
def index():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT title FROM event")
	all_events = [tup[0] for tup in cursor.fetchall()]

	return render_template('index.html', all_events = all_events)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
	next = request.args.get('next')
	form = SigninForm(request.form)

	if request.method == 'POST':
		if form.validate():
			session['username'] = form.my_username.data
			if request.form.get('next') != None:
				return redirect(request.form.get('next'))
			else:
				return redirect(url_for('profile'))
		# else fall through and render signin form again

	return render_template('signin.html', form=form, next=next)

@app.route('/signup', methods = ['GET', 'POST'])
def sign_up():
	connection = mysql.get_db()
	cursor = connection.cursor()

	form = SignupForm(request.form)
	if request.method == "POST":
		if form.validate() == False:
			flash('Fill in required fields')
			return render_template('signup.html', form=form)
		else:
			password_hash = generate_password_hash(form.password.data)
			attr = (form.firstname.data, form.lastname.data, form.email.data, form.username.data, password_hash)
			cursor.callproc('CreateUser', (attr[0], attr[1], attr[2], attr[3], attr[4]))
			connection.commit()

			session['username'] = form.username.data
			return redirect(url_for('profile'))


			return("thank you for signing up!")
	elif request.method == 'GET':
		return render_template('signup.html', form=form)

@app.route('/signout')
def signout():
	if not session['username']:
		return redirect(url_for('signin'))
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
	form = interest_form(request.form)
	categories = form.categories.data

	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT uid FROM User WHERE username = '{}'" .format(session['username']))
	uid = cursor.fetchall()[0][0]

	if request.method == "POST":		
		cursor.execute("DELETE FROM HasInterests WHERE HasInterests.uid = '{}'" .format(uid))
		connection.commit()
		for category in categories:
			cursor.execute("INSERT INTO HasInterests(uid, categoryName) VALUES('{}', '{}')".format(uid, category))
			connection.commit()

	cursor.execute("SELECT categoryName FROM HasInterests WHERE uid ={}".format(uid))
	pre_selected = [ tup[0] for tup in cursor.fetchall()]

	form.categories.data = pre_selected

		# return render_template('settings.html', form=form, pre_selected=pre_selected)

	return render_template('settings.html', form=form)

@app.route('/profile')
def profile():
	if not session['username']:
		return redirect(url_for('signin'))

	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT uid FROM User WHERE username='{}'".format(session['username']))
	uid = cursor.fetchall()[0][0]

	cursor.execute("SELECT Event.eid, title, startDate, building, lowPrice, highPrice FROM Event, EventCreated WHERE EventCreated.uid = '{}' AND EventCreated.eid = Event.eid".format(uid))
	created_events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()]


	cursor.execute("SELECT Event.eid, title, startDate, building, lowPrice, highPrice FROM IsInterestedIn, User, Event WHERE IsInterestedIn.uid = User.uid AND User.username = '{}' AND Event.eid = IsInterestedIn.eid".format(session['username']))
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()]

	user = cursor.execute("SELECT uid From User Where username = '{}'".format(session['username']))
	if user is None:
		return redirect(url_for('signin'))
	else:
		return render_template('profile.html', events=events, created_events=created_events)

@app.route('/eventcreate', methods=['GET','POST'])
def eventcreate():
	if not session.get('username'):
		return redirect(url_for("signin", next=request.url_rule))

	connection = mysql.get_db()
	cursor = connection.cursor()

	# get uid
	cursor.execute("SELECT uid FROM User WHERE username='{}'".format(session['username']))
	uid = cursor.fetchall()[0][0]

	form = CreateEventForm(request.form)
	error = None

	eid = request.args.get('eid')
	if request.method == "GET" and eid:
		attrs = "eid, title, description, building, addrAndStreet, city, zipcode, startDate, startTime, endDate, endTime, lowPrice, highPrice"
		cursor.execute("SELECT {} FROM Event WHERE eid={}".format(attrs, eid))
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

		sd = data[7]
		st = data[8]
		ed = data[9]
		et = data[10]
		startTime = "{}:{}".format(st.seconds//3600, (st.seconds//60)%60)
		endTime = "{}:{}".format(et.seconds//3600, (et.seconds//60)%60)
		form.startDate.data = "{}/{}/{} {}".format(sd.month, sd.day, sd.year, datetime.strptime(startTime, "%H:%M").strftime("%I:%M %p"))
		form.endDate.data = "{}/{}/{} {}".format(ed.month, ed.day, ed.year, datetime.strptime(endTime, "%H:%M").strftime("%I:%M %p"))

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

				# add lat and lng after zipcode
				if field.name == 'zipcode':
					attr_list.append(form.lat)
					attr_list.append(form.lng)

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

			cursor.execute("SELECT eid FROM Event WHERE title='{}' AND startDate='{}' AND startTime='{}'".format(form.title.data, form.start[0], form.start[1]))
			id = cursor.fetchall()[0][0]
				
			connection.commit()

			return redirect(url_for('get_event', id=id))

	return render_template('eventcreate.html', form=form, error=error)

MAX_PER_PAGE = 20

@app.route('/browse/', methods=['GET', 'POST'])
@app.route('/browse/<filter_path>', methods=['GET', 'POST'])
def browse(filter_path = None):
	form = searchBy(request.form)
	if request.method == 'POST':
		filter_path = ""
		searchTerm = None
		if request.form.get('homeSearch'):
			searchTerm = request.form.get('homeSearch')
		else:
			searchTerm = form.searchTerm.data
			if form.category.data and form.category.data != 'All Categories':
				if filter_path != "":
					filter_path += "--"
				filter_path += "c%{}".format(cat_to_url_filter(form.category.data))
			if form.eventType.data and form.eventType.data != 'All Event Types':
				if filter_path != "":
					filter_path += "--"
				filter_path += "e%{}".format(cat_to_url_filter(form.eventType.data))
			if form.price.data and form.price.data != 'All Prices':
				if filter_path != "":
					filter_path += "--"
				filter_path += "p%{}".format(form.price.data)
			if form.daterange.data:
				if filter_path != "":
					filter_path += "--"
				daterange = form.get_daterange()
				if daterange and daterange[0] and daterange[1]:
					filter_path += "d%{}&{}".format(daterange[0], daterange[1])
			
		if searchTerm:
			return redirect(url_for('browse', filter_path=filter_path, searchTerm=searchTerm))
		else:
			return redirect(url_for('browse', filter_path=filter_path))

	searchTerm = request.args.get('searchTerm')
	form.searchTerm.data = searchTerm
	# parse filter path
	category = None
	eventType = None
	price = None
	daterange = None
	if filter_path:
		for filter_str in filter_path.split('--'):
			key, val = filter_str.split('%')
			# category
			if key == 'c':
				category = url_to_cat_filter(val)
				form.category.data = category
			# event type
			elif key == 'e':
				eventType = url_to_cat_filter(val)
				form.eventType.data = eventType
			# price
			elif key == 'p':
				price = val
				form.price.data = price
			# date
			elif key == 'd':
				daterange = tuple(val.split('&'))
				form.set_daterange(daterange[0], daterange[1])
	if not category:
		form.category.data = 'All Categories'
	if not eventType:
		form.eventType.data = 'All Event Types'
	if not price:
		form.price.data = 'All Prices'

	connection = mysql.get_db()
	cursor = connection.cursor()

	page = request.args.get('page', type=int, default=1)

	# generate query with any filters if necessary
	attrs = "eid, title, startDate, building, lowPrice, highPrice"
	query = ""
	where_clause = ""
	if searchTerm or category or eventType or price or daterange:
		if searchTerm:
			if where_clause:
				where_clause += " AND "
			where_clause += "title LIKE '%{}%'".format(searchTerm)
		if category:
			if where_clause:
				where_clause += " AND "
			where_clause += "eid IN (SELECT eid FROM HasCategory WHERE categoryName='{}')".format(category)
		if eventType:
			if where_clause:
				where_clause += " AND "
			where_clause += "eid IN (SELECT eid FROM HasEventType WHERE eventType='{}')".format(eventType)
		if price:
			if where_clause:
				where_clause += " AND "
			if price == 'Free':
				where_clause += "lowPrice IS NOT NULL AND highPrice IS NOT NULL AND lowPrice = 0 AND highPrice = 0"
			elif price == 'Paid':
				where_clause += "lowPrice IS NOT NULL AND highPrice IS NOT NULL AND lowPrice <> 0 AND highPrice <> 0"
		if daterange and daterange[0] and daterange[1]:
			if where_clause:
				where_clause += " AND "
			where_clause += "DATEDIFF(startDate, '{}') >= 0 AND DATEDIFF(endDate, '{}') <= 0".format(daterange[0], daterange[1])
			
		query = "SELECT {} lowPrice, highPrice FROM Event WHERE {}".format(attrs, where_clause)
	else:
		query = "SELECT {} FROM Event".format(attrs)
	
	res_len = cursor.execute(query)

	start_row = MAX_PER_PAGE*(page-1)
	end_row = start_row+MAX_PER_PAGE if (start_row+MAX_PER_PAGE < res_len) else res_len
	events = [dict(eid=row[0],
                   title=row[1],
                   startDate=row[2],
                   building=row[3],
                   lowPrice=row[4],
                   highPrice=row[5]) for row in cursor.fetchall()[start_row:end_row]]

	# cursor.close()
	pagination = Pagination(page=page, total=res_len, per_page=MAX_PER_PAGE, css_framework='bootstrap3')
	return render_template('events.html', events=events, pagination=pagination, form=form)

@app.route('/communities')
def communities():
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT cid, name, uid FROM Community")
	communities = [dict(cid=row[0],
                   name=row[1].replace('/', '\''), uid=row[2]) for row in cursor.fetchall()]
	cursor.close()

	return render_template('communities.html', communities=communities)

@app.route('/communitycreate', methods=['GET','POST'])
def create_community():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT name FROM Category")
	categories = [(row[0], row[0].replace(' ', '-').lower()) for row in cursor.fetchall()]

	if not session.get('username'):
		return redirect("/signin")
	else:
		cursor.execute("SELECT uid FROM User WHERE username='{}'".format(session['username']))
		uid = cursor.fetchall()[0][0]
	
	form = CreateCommunityForm(request.form)
	
	if request.method == "POST":
		if form.validate() == False:
			flash('Fill in required fields')
			return render_template('community_create.html', form=form, categories=categories)
		else:
			s = ","
			form.categories.data = s.join(map(str, form.categories.data))
			
			cursor.callproc('CreateCommunity', (form.name.data.replace('\'', '/'), uid, form.categories.data))
			cursor.execute("SELECT cid FROM Community WHERE name='{}'".format(form.name.data.replace('\'', '/')))
			cid = cursor.fetchall()[0][0]
			cursor.execute("INSERT INTO IsCommunityMember(uid, cid) VALUES({}, {})".format(uid, cid))
			cursor.close()
			connection.commit()
			return redirect(url_for('communities'))
 
	elif request.method == 'GET':
    		return render_template('community_create.html', form=form, categories=categories)

@app.route('/communities/category/<category>', methods=['GET','POST'])
def community_(category):
	connection = mysql.get_db()
	cursor = connection.cursor()

	page = request.args.get('page', type=int, default=1)
	category = ",".join([ (word.capitalize() if word != 'and' else word) for word in category.split('-') ])
	res_len = cursor.execute("SELECT cid, name, uid FROM Community WHERE (cid) IN (SELECT cid FROM CommunityCategories WHERE categoryName='{}')".format(category))
	start_row = MAX_PER_PAGE*(page-1)
	end_row = start_row+MAX_PER_PAGE if (start_row+MAX_PER_PAGE < res_len) else res_len
	communities = [dict(cid=row[0],
                   name=row[1].replace('/', '\''), uid=row[2]) for row in cursor.fetchall()[start_row:end_row]]
	cursor.close()

	pagination = Pagination(page=page, total=res_len, per_page=MAX_PER_PAGE, css_framework='bootstrap3')
	return render_template('communities.html', communities=communities, pagination=pagination)

@app.route('/communities/communityid/<id>', methods=['GET','POST'])
def community(id):
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT name, uid FROM Community WHERE cid='{}'".format(id))
	info_tuple = cursor.fetchall()[0]
	cname = info_tuple[0]
	uid = info_tuple[1]
	
	cursor.execute("SELECT categoryName FROM CommunityCategories WHERE cid='{}'".format(id))
	categories_list = cursor.fetchall()
	community_categories = ""
	for row in categories_list:
		community_categories += row[0]
		community_categories += ","
	community_categories = community_categories[:-1]

	cursor.execute("SELECT username FROM User WHERE uid ='{}'".format(uid))
	username = cursor.fetchall()[0][0]

	cursor.execute("SELECT username FROM User WHERE uid IN (SELECT uid FROM isCommunityMember WHERE cid ='{}')".format(id))
	member_list = cursor.fetchall()
	members = []
	for row in member_list:
		members.append(row[0])
	
	if session.get('username'):
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		userid = cursor.fetchall()[0][0]
		length = cursor.execute("SELECT * FROM IsCommunityMember WHERE cid ='{}' AND uid='{}'".format(id,userid))
		cursor.close()
		if length:
			return render_template("community_joined.html", cid=id, cname=cname, community_categories=community_categories, username=username, members=members)
	cursor.close()
	return render_template("community.html", cid=id, cname=cname, community_categories=community_categories, username=username, members=members)

@app.route('/communities/communityid/<id>/joined')
def is_communitymember(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	if not session.get('username'):
		return redirect(url_for('signin'))
	else:
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		uid = cursor.fetchall()[0][0]
		cursor.execute("INSERT INTO IsCommunityMember(uid, cid) VALUES({}, {})".format(uid, id))

		cursor.execute("SELECT name, uid FROM Community WHERE cid='{}'".format(id))
		info_tuple = cursor.fetchall()[0]
		cname = info_tuple[0]
		uid = info_tuple[1]
	
		cursor.execute("SELECT categoryName FROM CommunityCategories WHERE cid='{}'".format(id))
		categories_list = cursor.fetchall()
		community_categories = ""
		for row in categories_list:
			community_categories += row[0]
			community_categories += ","
		community_categories = community_categories[:-1]

		cursor.execute("SELECT username FROM User WHERE uid ='{}'".format(uid))
		username = cursor.fetchall()[0][0]

		cursor.execute("SELECT username FROM User WHERE uid IN (SELECT uid FROM isCommunityMember WHERE cid ='{}')".format(id))
		member_list = cursor.fetchall()
		members = []
		for row in member_list:
			members.append(row[0])
		connection.commit()
		return render_template("community_joined.html", cid=id, cname=cname, community_categories=community_categories, username=username, members=members)

@app.route('/communities/communityid/<id>/unjoined')
def is_not_communitymember(id):
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
	uid = cursor.fetchall()[0][0]
	cursor.execute("DELETE FROM isCommunityMember WHERE uid = '{}' AND cid = '{}'".format(uid, id))
	connection.commit()
	return redirect(url_for('community', id=id))

@app.route('/communities/communityid/<id>/members')
def community_member_list(id):
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT username FROM User WHERE uid IN (SELECT uid FROM isCommunityMember WHERE cid ='{}')".format(id))
	member_list = cursor.fetchall()
	members = []
	for row in member_list:
		members.append(row[0])

	cursor.execute("SELECT name FROM Community WHERE cid='{}'".format(id))
	cname = cursor.fetchall()[0][0];
	return render_template("community_members.html", cid=id, members=members, cname=cname)

@app.route('/browse/eventid/<id>', methods=['get','post'])
def get_event(id):
	connection = mysql.get_db()
	cursor = connection.cursor()

	# add event as registered view for logged in user if not done so already
	if session.get('username'):
		retlen = cursor.execute("SELECT uid FROM User WHERE username = '{}'" .format(session['username']))
		if retlen > 0:
			uid = cursor.fetchall()[0][0]
			retlen = cursor.execute("SELECT uid FROM HasRegisteredViews WHERE uid = {} AND eid = {}".format(uid, id))
			if retlen == 0:
				cursor.execute("INSERT INTO HasRegisteredViews(uid, eid) VALUES ({}, {})".format(uid, id)) 
				connection.commit()
	else:
		retlen = cursor.execute("SELECT nonUserViews FROM Event WHERE eid = {}".format(id))
		if retlen > 0:
			nonUserViews = cursor.fetchall()[0][0]
			nonUserViews += 1
			cursor.execute("UPDATE Event SET nonUserViews = {} WHERE eid = {}".format(nonUserViews, id))
			connection.commit()

	editPermission = False
	already_interested = None
	if session.get('username'):
		# check if user can edit and delete
		if session['username'] == 'admin':
			editPermission = True
		else:
			reslen = cursor.execute("SELECT username FROM User WHERE uid = (SELECT uid FROM EventCreated WHERE eid={})".format(id))
			if reslen > 0 and cursor.fetchall()[0][0] == session['username']:
				editPermission = True

		# check if user is already interested in event
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		uid = cursor.fetchall()[0][0]

		reslen = cursor.execute("SELECT eid FROM IsInterestedIn WHERE uid = '{}' AND eid = '{}'".format(uid,id))
		if reslen > 0:
			already_interested = 1

	attrs = "eid, title, description, building, addrAndStreet, city, zipcode, startDate, startTime, endDate, endTime, lowPrice, highPrice, nonUserViews"
	cursor.execute("SELECT {} FROM Event WHERE eid='{}'".format(attrs, id))
	events = [dict(eid=row[0],
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
	cursor.close()

	return render_template('event.html', event=events, editPermission=editPermission, already_interested=already_interested)

@app.route('/deleteevent')
def delete_event(eid=None, next = None):
	eid = request.args.get('eid')
	next = request.args.get('next')
	if eid and next:
		connection = mysql.get_db()
		cursor = connection.cursor()
		cursor.execute("DELETE FROM Event WHERE eid={}".format(eid))
		connection.commit()

		if 'browse' in next:
			return redirect(next)
		else:
			return redirect(url_for('browse'))
	
@app.route('/browse/eventid/<id>/interested')
def is_interested(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	if not session.get('username'):
		return redirect(url_for('signin'))
	else:
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		uid = cursor.fetchall()[0][0]
		curr_url = request.referrer
		curr = curr_url.split('/')[-1]
		new_url = curr_url.split('//')[1]
		cursor.execute("INSERT INTO IsInterestedIn(uid, eid) VALUES({}, {})".format(uid, curr))
		connection.commit()
		return redirect(url_for('get_event', id=id))
		# return redirect(url_for('browse'))
		 # , session=session, curr=curr, uid=uid)

@app.route('/browse/eventid/<id>/uninterested')
def is_uninterested(id):
	connection = mysql.get_db()
	cursor = connection.cursor()
	if not session.get('username'):
		return redirect(url_for('signin'))
	else:
		cursor.execute("SELECT uid FROM User where username = '{}' LIMIT 1".format(session['username']))
		uid = cursor.fetchall()[0][0]
		curr_url = request.referrer
		curr = curr_url.split('/')[-1]
		cursor.execute("DELETE FROM IsInterestedIn WHERE uid = '{}' AND eid = '{}'".format(uid, curr))
		connection.commit()
		return redirect(url_for('get_event', id=id))

@app.context_processor
def googlelocfilter():
	def _googlelocfilter(building, addr, city, cityzip):
		locstr = "{}, {}, IL, {}".format(addr, city, cityzip)
		gmaps = googlemaps.Client(key=GMAPS_KEY)
		ret = gmaps.geocode(address=locstr)
		lng = 0.0
		lat = 0.0
		if len(ret) > 0:
			lat = "{0:.7f}".format(ret[0]['geometry']['location']['lat'])
			lng = "{0:.7f}".format(ret[0]['geometry']['location']['lng'])
			cordstr = "{},{}".format(lat,lng)
			addrmod = addr.replace(" ", "+")
			buildingmod = building.replace(" ", "+")
			locstr2 = buildingmod+"+"+addrmod
			locstr3 = locstr2+",+"+str(cityzip)+",+USA"
			mapstr =  "https://maps.google.co.uk/maps?f=q&source=s_q&hl=en&geocode=&q="+locstr2+"&sll="+cordstr+"&ie=UTF8&hq=&hnear="+locstr3+"&t=m&z=17"+"&ll="+cordstr+"&output=embed"
			return mapstr
		else:
			return ""
	return dict(googlelocfilter=_googlelocfilter)

@app.route('/eventsnearme', methods=['get','post'])
def events_near_me():
	if not session.get('username'):
		return redirect(url_for("signin", next=request.url_rule))
	
	form = EventsNearMeForm(request.form)

	if request.args.get('radius'):
		form.radius.data = request.args.get('radius')
	if request.args.get('limit'):
		form.limit.data = request.args.get('limit')
	
	if request.method=='post':
		return redirect(url_for('events_near_me', radius=form.radius.data, limit=form.limit.data))
		

	connection = mysql.get_db()
	cursor = connection.cursor()
	
	# get latitude and longitude of user's ip address
	user_loc_tup = None
	user_loc = None

	provided_ips = request.headers.getlist("X-Forwarded-For")
	ip = provided_ips[0] if len(provided_ips) > 0 else 'me'
	g = ipinfo(ip)
	if g and g.latlng and len(g.latlng) > 0:
		user_loc_tup = tuple(g.latlng)

	if user_loc_tup == None or len(user_loc_tup) == 0:
		user_loc_tup = (40.1164, -88.2434) # lat/lng of Champaign
	user_loc = {"lat": user_loc_tup[0], "lng": user_loc_tup[1]}

	# calculate distances
	locs = []
	attrs = "eid, title, lat, lng"
	retlen = cursor.execute("SELECT {} FROM Event".format(attrs))
	if retlen > 0:
		for row in cursor.fetchall():
			eid = row[0]
			title = row[1]
			event_loc = (row[2], row[3])

			if event_loc and event_loc[0] and event_loc[1]:
				dist = haversine(user_loc_tup, event_loc, miles=True)
				if dist <= float(form.radius.data):
					dict = {"eid": eid, "title": title, "dist": dist, "loc": {"lat": event_loc[0], "lng": event_loc[1]}}
					locs.append(dict)
		locs.sort(key=lambda loc: loc["dist"])
		end_row = int(form.limit.data) if len(locs) >= int(form.limit.data) else len(locs)
		markers = locs[0:end_row]

	return render_template('events_near_me.html', user_loc=user_loc, markers=markers, form=form, key=GMAPS_KEY)

def update_locs():
	connection = mysql.get_db()
	cursor = connection.cursor()

	attrs = "eid, addrAndStreet, city, zipcode"
	cursor.execute("SELECT {} FROM Event".format(attrs))
	for row in cursor.fetchall():
		eid = row[0]
		addrAndStreet = row[1]
		city = row[2]
		zipcode = row[3]

		gmaps = googlemaps.Client(key=GMAPS_KEY)
		ret = gmaps.geocode(address=locstr)
		if len(ret) > 0:
			lat = "{0:.7f}".format(ret[0]['geometry']['location']['lat'])
			lng = "{0:.7f}".format(ret[0]['geometry']['location']['lng'])

			cursor.execute("UPDATE Event SET lat = {}, lng = {} WHERE eid={}".format(lat, lng, eid))
		connection.commit()

@app.route('/autocomplete')
def autocomplete():
	connection = mysql.get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT title FROM Event")
	all_events = [tup[0] for tup in cursor.fetchall()]
	return jsonify(json_list=all_events) 

