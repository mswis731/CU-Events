from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By

import re

url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi"
driver = webdriver.PhantomJS()

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
		location = location_div.find("h6", {"itemprop": "name"}).find("a").text.strip()

		address_p = location_div.find("p", {"itemprop": "address"})
		street_sp = address_p.find("span", {"itemprop": "streetAddress"})
		city_sp = address_p.find("span", {"itemprop": "addressLocality"})
		state_sp = address_p.find("span", {"itemprop": "addressRegion"})
		zipcode_sp = address_p.find("span", {"itemprop": "postalCode"})
		street = street_sp.text.strip() if street_sp else ""
		city = city_sp.text.strip() if city_sp else ""
		state = state_sp.text.strip() if state_sp else ""
		zipcode = zipcode_sp.text.strip() if zipcode_sp else ""

		start_date = event_soup.find("div", {"itemprop": "startDate"})["content"]

		price_div = event_soup.find("div", {"id": "event-price"})
		price_text = ""
		if price_div:
			price_text = price_div.find("p").text.strip()

		description_div = event_soup.find("div", class_="section-block description")
		description = description_div.find("p", {"itemprop": "description"}).text.strip()
		description_ps = description_div.findAll("p")
		categories = [ link.text.strip() for link in description_ps[len(description_ps)-1].findAll("a")]

		"""
		print("URL: {}".format(event_url))
		print("Title: {}".format(title))
		print("Location: {}".format(location))
		print("Full Address: {} {} {} {}".format(street, city, state, zipcode))
		print("Start Date: {}".format(start_date))
		print("Price Text: {}".format(price_text))
		print("Description: {}".format(description))
		print("Categories: {}".format(categories))
		print()
		"""

	next_link = soup.find("span", class_="nav next")
	if next_link:
		url = "http://eventful.com" + next_link.find("a")["href"]
	else:
		break
