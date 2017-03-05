from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By

start = 'https://www.eventbrite.com/d/il--champaign/events/?page=1'

driver = webdriver.PhantomJS()
driver.get(start)
soup = BeautifulSoup(driver.page_source, 'html.parser')
total_pages = int(soup.find("ul", class_="pagination__navigation-group").find("li", class_="js-page-link js-last-page show-large").find("a").text.strip())

url = 'https://www.eventbrite.com/d/il--champaign/events/?page={}' 
index = 1
for page in range(1, (total_pages+1)):
	driver.get(url.format(page))
	soup = BeautifulSoup(driver.page_source, 'html.parser')

	event_divs = soup.find_all("div", class_="list-card-v2 l-mar-top-2 js-d-poster")
	for event in event_divs:
		title = event.find("div", class_="list-card__title").text.strip()
		venue = event.find("div", class_="list-card__venue").text.strip()
		price = event.find("span", class_="list-card__label").text.strip()
		date = event.find("time", class_="list-card__date").text.strip()
		tags = [ link.text.strip() for link in event.find("div", class_="list-card__tags").find_all("a") ]
	
		print("{}.".format(index))
		print("Title: {}".format(title))
		print("Venue: {}".format(venue))
		print("Price: {}".format(price))
		print("Date: {}".format(date))
		print("Categories/Event Types: {}\n".format(tags))
		
		index += 1
driver.close()
