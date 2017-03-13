from app import app, mysql
from app.crawlers.mappings import map_months, map_categories, map_event_types 
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from decimal import Decimal

def crawl():
	# connect to database
	connection = mysql.get_db()
	cursor = connection.cursor()

	driver = webdriver.PhantomJS()

	url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi"
	#url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi&page_number=6"
	
	while 1:
		driver.get(url)
		soup = BeautifulSoup(driver.page_source, 'html.parser')
	
		event_trs = soup.findAll("tr")
		for event in event_trs:
			# open event page
			event_url = event.find("td", class_="event-info").find("h3").find("a")["href"]
			individual_event(driver, connection, cursor, event_url, 0)

		next_link = soup.find("span", class_="nav next")
		if next_link:
			url = "http://eventful.com" + next_link.find("a")["href"]
		else:
			break

def update_crawled_events():
	# connect to database
	connection = mysql.get_db()
	cursor = connection.cursor()

	driver = webdriver.PhantomJS()

	cursor.execute("SELECT url FROM EventCrawled WHERE site = 'Eventful'")
	urls = [ row[0] for row in cursor.fetchall() ]
	for url in urls:
		individual_event(driver, connection, cursor, url, 1)

def individual_event(driver, connection, cursor, event_url, update):
	driver.get(event_url)
	event_soup = BeautifulSoup(driver.page_source, 'html.parser')
	
	title = event_soup.find("div", class_="header large").find("h1").findAll("span")[0].text.strip()
	
	location_div = event_soup.find("div", class_="location")
	building = location_div.find("h6", {"itemprop": "name"}).find("a").text.strip()
	
	# TODO: street doesn't always just contain number and street name
	# TODO: street name and abbrv. not always capitalized
	address_p = location_div.find("p", {"itemprop": "address"})
	street_sp = address_p.find("span", {"itemprop": "streetAddress"})
	city_sp = address_p.find("span", {"itemprop": "addressLocality"})
	zipcode_sp = address_p.find("span", {"itemprop": "postalCode"})
	street = street_sp.text.strip() if street_sp else None
	city = city_sp.text.strip() if city_sp else None
	zipcode = zipcode_sp.text.strip() if zipcode_sp else None
	
	dates = event_soup.find("div", {"itemprop": "startDate"})
	dates_text = dates.text.lower().strip()
	# clean up dates_text
	replacements = [ ('\xa0', ' '), ('\n', ' '), (',', '') ]
	for k, v in replacements:
		dates_text = dates_text.replace(k, v)
	dates_list = dates_text.split(' ')
	extra_terms = ["", "(on", "various", "days)"]
	for term in extra_terms:
		count = dates_list.count(term)
		for i in range(count):
			dates_list.remove(term)
	# convert to YYYY-MM-DD and HH:MM:SS format
	start_date = None
	start_time = "00:00:00" # default all day
	end_date = None
	end_time = "23:59:00" # default all day
	size = len(dates_list)
	try:
		if size == 7 or size == 6 or size == 3:
			start_date = "{}-{}-{}".format(dates_list[2], map_months[dates_list[0]], dates_list[1].zfill(2))
			if size == 7:
				end_date = "{}-{}-{}".format(dates_list[6], map_months[dates_list[4]], dates_list[5])
			elif size == 6:
				times_list = dates_list[4].split(':')
				if dates_list[5] == 'pm' and times_list[0] != 12:
					times_list[0] = str(int(times_list[0])+12)
				times_list[0] = times_list[0].zfill(2) # add leading zero if necessary
				start_time = "{}:{}:00".format(times_list[0], times_list[1])
			elif size == 3:
				end_date = start_date
	except:
		pas
	# skip if starting time is not found
	if not title or not start_date:
		continu
	price_div = event_soup.find("div", {"id": "event-price"})
	price_text = None
	prices = []
	low_price = None
	high_price = None
	if price_div:
		price_text = price_div.find("p").text.strip()
		price_list = price_text.lower().split(" ")
		for term in price_list:
			try:
				if term == 'free':
					prices.append(0)
				elif term[0] == '$' and Decimal(term[1:]):
					prices.append(Decimal(term[1:]))
				elif Decimal(term):
					prices.append(Decimal(term))
			except:
				pass
		if len(prices):
			low_price = min(prices)
			high_price = max(prices)
	description_div = event_soup.find("div", class_="section-block description")
	description = description_div.find("p", {"itemprop": "description"}).text.strip()
	if description == "There is no description for this event.":
		description = None
	description_ps = description_div.findAll("p")
	categories_list = [ link.text.strip().lower() for link in description_div.findAll(text=re.compile("Categories:"))[0].parent.findAll("a")]
	categories = []
	event_types = []
	for category in categories_list:
		if map_categories.get(category) and map_categories[category] not in categories:
			categories.append(map_categories[category])
		"""
		else:
			print("Category not mapped: {}".format(category))
		"""
		if map_event_types.get(category) and map_event_types[category] not in event_types:
			event_types.append(map_event_types[category])
		"""
		else:
			print("Type not mapped: {}".format(category))
		"""
	if len(categories) == 0:
		categories.append("Other")
	if len(event_types) == 0:
		event_types.append("Other")
	
	organizer = None
	
	if not update:
		cursor.callproc('CreateCrawledEvent', (title,
												description,
												building,
												street,
												city,
												zipcode,
												start_date,
												start_time,
												end_date,
												end_time,
												low_price,
												high_price,
												event_url,
												organizer,
												"Eventful"))
		for category in categories:
			cursor.callproc('LinkEventCategory', (title,
													start_date,
													start_time,
													category))
		for e_type in event_types:
			cursor.callproc('LinkEventType', (title,
												start_date,
												start_time,
												e_type))
	else:
		cursor.callproc('UpdateCrawledEvent', (title,
												description,
												building,
												street,
												city,
												zipcode,
												start_date,
												start_time,
												end_date,
												end_time,
												low_price,
												high_price,
												event_url))
		
	connection.commit()
	print(event_url)

if __name__ == "__main__":
	update = 1
	if not update:
		crawl()
	else:
		update_crawled_events()
		
