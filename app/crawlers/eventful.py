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

	#url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi"
	url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi&page_number=6"
	driver = webdriver.PhantomJS()
	
	index = 0
	while 1:
		driver.get(url)
		soup = BeautifulSoup(driver.page_source, 'html.parser')
	
		event_trs = soup.findAll("tr")
		for event in event_trs:
			# open event page
			event_url = event.find("td", class_="event-info").find("h3").find("a")["href"]
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
			# convert to YYYY-MM-DD HH:MM:SS format
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
						if dates_list[5] == 'pm':
							times_list[0] = str(int(times_list[0])+12)
						times_list[0] = times_list[0].zfill(2) # add leading zero if necessary
						start_time = "{}:{}:00".format(times_list[0], times_list[1])
					elif size == 3:
						end_date = start_date
			except:
				pass

			start = None
			end = None
			if start_date:
				start = "{} {}".format(start_date, start_time)
			if end_date:
				end = "{} {}".format(end_date, end_time)
					
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
				else:
					print("Category not mapped: {}".format(category))
				if map_event_types.get(category) and map_event_types[category] not in event_types:
					event_types.append(map_event_types[category])
				else:
					print("Type not mapped: {}".format(category))
			"""
			print()
			print(categories)
			print(event_types)
			print()
			"""
				

			organizer = None
			
			cursor.callproc('CreateCrawledEvent', (title,
												   description,
												   building,
												   street,
												   city,
												   zipcode,
												   start,
												   end,
												   low_price,
												   high_price,
												   url,
												   organizer))
			connection.commit()
	
			"""
			print(index)
			print("URL: {}".format(event_url))
			print("Title: {}".format(title))
			print("Building: {}".format(building))
			print("Street: {}".format(street))
			print("City: {}".format(city))
			print("Zipcode: {}".format(zipcode))
			print("Start: {}".format(start))
			print("End: {}".format(end))
			print("Price text: {}".format(price_text))
			print("Prices: {}".format(prices))
			print("Low Price: {}".format(low_price))
			print("High Price: {}".format(high_price))
			print("Description: {}".format(description))
			print("Categories: {}".format(categories_list))
			print()
			index += 1
			"""
	
		next_link = soup.find("span", class_="nav next")
		if next_link:
			url = "http://eventful.com" + next_link.find("a")["href"]
		else:
			break

if __name__ == "__main__":
	crawl()
