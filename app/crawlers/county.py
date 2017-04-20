"""
import sys
#goes back two levels so that we can import app 
sys.path.append('../../')
"""

from app import app, mysql, GMAPS_KEY
from app.crawlers.mappings import map_months, map_times, map_categories, map_event_types
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
import re
import googlemaps

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
		#events = soup.find_all("div", class_="col-sm-2")
		#print(len(events))

		lists = soup.find_all("div", class_="event-detail-box")
		for list_ in lists:
			title = list_.find("a").contents[0]
			print(title)
			event_urls = list_.find("a")["href"]  
			driver.get("http://www.visitchampaigncounty.org/" + event_urls)
			event_soup = BeautifulSoup(driver.page_source, "html.parser")
			#print(event_soup.find("h4"))
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

			print(addrAndStreet, city, zipcode, lat, lng)

			time_general = event_soup.find("li", class_="box date border-right").getText()
			#print((time_general).split('\n'))
			year = time_general.split('\n')[2].split(" ")[3]
			month =time_general.split('\n')[2].split(" ")[1]
      
			month = map_months[month]

			date = time_general.split('\n')[2].split(" ")[2][:-1]

			full_date = "{}-{}-{}".format(year, month, date) 
			print(full_date)
  
			start_time = "00:00:00"
			end_time = "23:59:00"
			start_t = start_time
			end_t = end_time
			if "Starts" in time_general.split('\n')[3]:
				start_time = time_general.split('\n')[3].split(" ")[2]
				#print("start_time" +start_time)
  
				start_t = map_times[start_time]
				#print("start_t:" + start_t)
			else:
				start_time = time_general.split('\n')[3].split(" ")[0]
				start_t = map_times[start_time]
				#print("start_t: " + start_t)
				end_time = time_general.split('\n')[3].split(" ")[2]
				end_t = map_times[end_time]
				#print("end_t: " + end_t)

			#add a check to see if start date and end date are different
			start_date = "{} {}".format(full_date, start_t)
			end_date = "{} {}".format(full_date, end_t)
			print(start_date)
			print(end_date)

			event_type = None
			category = None
  
			low_price = 0;
			high_price = 0;
			price_general =  event_soup.find("li", class_="box tickte border-right").getText()
			price_split = (price_general.split('\n'))[2]
			print(low_price, high_price)
			if 'Buy Tickets' in price_split:
				ticket_url = event_soup.find("li", class_="box tickte border-right").find("span", class_="site-link").find("a")["href"]
         
			if (url == "http://www.visitchampaigncounty.org/events/category/22/exhibits") or (url == "http://www.visitchampaigncounty.org/events/category/16/festivals-and-fairs"):
				event_type = map_event_types[url]
				category = "Other"
				print (event_type)
			else:
				category = map_categories[url]
				event_type = "Other"
				print(category)

			#fix description to get rid of including unneccesary css properties 
			description =  event_soup.find("div", class_="panel-body").getText()
			print(description)

			event_url = "http://www.visitchampaigncounty.org/" + event_urls
			cursor.callproc('CreateCrawledEvent', (title,
      										 	   description,
      										  	   building,
      										 	   addrAndStreet,
      										 	   city,
      										 	   zipcode,
      										 	   lat,
      										 	   lng,
      										 	   full_date,
                           						   start_t,
      										 	   full_date,
                           						   end_t,
      										 	   low_price,
      										 	   high_price,
      										 	   event_url,
      										 	   "visitchampaigncounty",
      										 	   category,
      										 	   event_type))
			connection.commit()


if __name__ == "__main__":
  crawl()
