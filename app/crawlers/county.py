from app import app, mysql, GMAPS_KEY
from app.crawlers.mappings import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
import re
import googlemaps
from datetime import datetime
from decimal import Decimal

def crawl():
	connection = mysql.get_db()
	cursor = connection.cursor()

	urls = [ "http://www.visitchampaigncounty.org/events/category/14/arts-and-theater",
			 "http://www.visitchampaigncounty.org/events/category/22/exhibits",
			 "http://www.visitchampaigncounty.org/events/category/21/family---friendly",
			 "http://www.visitchampaigncounty.org/events/category/16/festivals-and-fairs",
			 "http://www.visitchampaigncounty.org/events/category/71/food-and-drink",
			 "http://www.visitchampaigncounty.org/events/category/19/history-and-education",
			 "http://www.visitchampaigncounty.org/events/category/15/music",
			 "http://www.visitchampaigncounty.org/events/category/17/nature-and-outdoors",
			 "http://www.visitchampaigncounty.org/events/category/18/sports"] 
	driver = webdriver.PhantomJS()
 
	for url in urls:
		driver.get(url)
		soup = BeautifulSoup(driver.page_source, 'html.parser')

		lists = soup.find_all("div", class_="event-detail-box")
		for list_ in lists:
			title = list_.find("a").contents[0]
			event_urls = list_.find("a")["href"]  
			driver.get("http://www.visitchampaigncounty.org/" + event_urls)
			event_soup = BeautifulSoup(driver.page_source, "html.parser")
			location_general = event_soup.find("li", class_="box place border-right").getText() 
			building = location_general.split('\n')[2]
			addrAndStreet = location_general.split('\n')[3] 
			city = location_general.split('\n')[4].split(',')[0]
			zipcode = location_general.split('\n')[4].split(" ")[2]

			lat = None
			lng = None

			locstr = "{}, {}, IL, {}".format(addrAndStreet, city, zipcode)
			gmaps = googlemaps.Client(key=GMAPS_KEY)
			ret = gmaps.geocode(address=locstr)
			if len(ret) > 0:
				# look for minor errors in address
				g_street_num = ""
				g_street_name = ""
				g_city = ""
				g_zipcode = ""
				for dict in ret[0]['address_components']:
					if 'street_number' in dict['types']:
						g_street_num = dict['short_name']
					elif 'route' in dict['types']:
						g_street_name = dict['short_name']
					elif 'locality' in dict['types']:
						g_city = dict['short_name']
					elif 'postal_code' in dict['types']:
						g_zipcode = dict['short_name']
		
				if (g_street_num and g_street_name and g_city and g_zipcode):
					addrAndStreet = g_street_num + " " + g_street_name
					city = g_city
					zipcode = g_zipcode
		
					lat = "{0:.7f}".format(ret[0]['geometry']['location']['lat'])
					lng = "{0:.7f}".format(ret[0]['geometry']['location']['lng'])

			time_general = event_soup.find("li", class_="box date border-right").getText().strip()
			date_str, time_str = time_general.split('\n')
			dt = datetime.strptime(date_str, '%A, %B %d, %Y')
			s_dt = None
			e_dt = None
			if 'Starts' in time_str:
				s_dt = datetime.strptime(time_str.split(' ')[2], '%I:%M%p')
			else:
				s_dt = datetime.strptime(time_str.split(' ')[0], '%I:%M%p')
				e_dt = datetime.strptime(time_str.split(' ')[2], '%I:%M%p')

			start_date = None
			end_date = None
			start_time = None
			end_time = None

			full_date = "{}-{}-{}".format(dt.year, dt.month, dt.day) 
			start_date = full_date
			if s_dt:
				start_time = "{}:{}:00".format(s_dt.hour, s_dt.minute)
			if e_dt:
				end_date = full_date
				end_time = "{}:{}:00".format(e_dt.hour, e_dt.minute)
				
			event_type = None
			category = None
  
			low_price = None;
			high_price = None;
			price_general =  event_soup.find("li", class_="box tickte border-right").getText().strip().lower()

			if price_general == 'free':
				low_price = 0
				high_price = 0
			else:
				prices = []
				s = None
				for i in range(len(price_general)):
					c = price_general[i]
					if s != None:
						if not (c.isdigit() or c == '.'):
							prices.append(Decimal(price_general[s+1:i]))
							s = None
					if s == None:
						if c == '$':
							s = i 
				if s != None:
					prices.append(Decimal(price_general[s+1:]))
				if len(prices) > 0:
					prices.sort()
					low_price = prices[0]
					high_price= prices[-1]

			"""
			if 'Buy Tickets' in price_split:
				ticket_url = event_soup.find("li", class_="box tickte border-right").find("span", class_="site-link").find("a")["href"]
			"""
         
			if (url == "http://www.visitchampaigncounty.org/events/category/22/exhibits") or (url == "http://www.visitchampaigncounty.org/events/category/16/festivals-and-fairs"):
				event_type = map_event_types[url]
				category = "Other"
			else:
				category = map_categories[url]
				event_type = "Other"

			description = "" 
			overview_h4 = event_soup.find("h4", class_="panel-title")
			panel_default = overview_h4.parent.parent
			try:
				panel_body = panel_default.findAll("div", class_="panel-body")[0]
				desc_p_tags = panel_body.findAll("p")
				for p_tag in desc_p_tags:
					text = p_tag.text.strip().replace('\n', '')
					ignore = '{' in text
					if not ignore and len(text) > 0:
						if description != "":
							description += "\n"
						description += text
			except:
				pass
			if description == "":
				description = None

			event_url = "http://www.visitchampaigncounty.org/" + event_urls

			"""
			print()
			print("url: {}".format(event_url))
			print("Title: {}".format(title))
			#print("Desc: {}".format(description))
			print("Location: {} {} {}\t({}, {})".format(addrAndStreet, city, zipcode, lat, lng))
			print("Start Date: {}\t Start Time: {}".format(start_date, start_time))
			print("End Date: {}\t End Time: {}".format(end_date, end_time))
			print("Price Range: ({}, {})".format(low_price, high_price))
			print("Category: {}\t Event Type: {}".format(category, event_type))
			print()
			"""

			cursor.callproc('CreateCrawledEvent', (title,
      										 	   description,
      										  	   building,
      										 	   addrAndStreet,
      										 	   city,
      										 	   zipcode,
      										 	   lat,
      										 	   lng,
      										 	   start_date,
                           						   start_time,
      										 	   end_date,
                           						   end_time,
      										 	   low_price,
      										 	   high_price,
      										 	   event_url,
      										 	   "visitchampaigncounty",
      										 	   category,
      										 	   event_type))
			connection.commit()

			print(event_url)


if __name__ == "__main__":
  crawl()
