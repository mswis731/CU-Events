from app import app, mysql
from app.crawlers.mappings import map_months, map_categories, map_event_types 
from bs4 import BeautifulSoup
from selenium import webdriver
import re

def crawl():
	# connect to database
	"""
	connection = mysql.get_db()
	cursor = connection.cursor()
	"""

	url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi"
	#url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi&page_number=6"
	driver = webdriver.PhantomJS()
	
	index = 0
	while 1:
		driver.get(url)
		soup = BeautifulSoup(driver.page_source, 'html.parser')
	
		event_trs = soup.find_all("tr")
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
			# convert to YYYY-MM-DD and HH:MM:SS format
			start_date = None
			start_time = None
			end_date = None
			end_time = None
			size = len(dates_list)
			try:
				if size == 7 or size == 6 or size == 3:
					start_date = "{}-{}-{}".format(dates_list[2], map_months[dates_list[0]], dates_list[1].zfill(2))
					if size == 7:
						end_date = "{}-{}-{}".format(dates_list[6], dates_list[5], map_months[dates_list[4]])
					if size == 6:
						times_list = dates_list[4].split(':')
						if dates_list[5] == 'pm':
							times_list[0] = str(int(times_list[0])+12)
						times_list[0] = times_list[0].zfill(2) # add leading zero if necessary
						start_time = "{}:{}:00".format(times_list[0], times_list[1])
			except:
				pass
					
			price_div = event_soup.find("div", {"id": "event-price"})
			price_range = None
			prices = []
			if price_div:
				price_text = price_div.find("p").text.strip()
				price_list = price_text.lower().split(" ")
				for term in price_list:
					try:
						if term == 'free':
							prices.append(0)
						elif term[0] == '$' and int(term[1:]):
							prices.append(int(term[1:]))
						# TODO: fix bug where decimal number is not recognized
						elif int(term):
							prices.append(int(term))
					except:
						pass
				#print(price_text)
				#print(prices)
	
			description_div = event_soup.find("div", class_="section-block description")
			description = description_div.find("p", {"itemprop": "description"}).text.strip()
			if description == "There is no description for this event.":
				description = None
			description_ps = description_div.findAll("p")
			categories_list = [ link.text.strip().lower() for link in description_div.findAll(text=re.compile("Categories:"))[0].parent.findAll("a")]
			#print(categories_list)

			categories = None
			event_type = None

			organizer = None
			
			"""
>>>>>>> e3302115d6ced21eee3bfd91b2c5fffcd7883935
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
												   price_range,
												   event_type,
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
			print("Start Date: {}".format(start_date))
			print("Start Time: {}".format(start_time))
			print("End Date: {}".format(end_date))
			print("End Date: {}".format(end_time))
			print("Prices: {}".format(price_range))
			print("Description: {}".format(description))
			print("Categories: {}".format(categories_list))
			print()
			index += 1
	
		next_link = soup.find("span", class_="nav next")
		if next_link:
			url = "http://eventful.com" + next_link.find("a")["href"]
		else:
			break

if __name__ == "__main__":
	crawl()
