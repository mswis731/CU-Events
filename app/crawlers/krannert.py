from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
import re

def crawl():

	url = "https://krannertcenter.com/calendar?date=2017-03"
	driver = webdriver.PhantomJS()

	index = 0
	
	while 1:
		driver.get(url)
		soup = BeautifulSoup(driver.page_source, 'html.parser')

		event_list = soup.find_all("span", class_="event-details")
		
		for event in event_list:
			eventURL = event.find("a")["href"]
			baseURL = "https://krannertcenter.com"
			fullEventLink = eventURL + baseURL

			driver.get(fullEventLink)
			soup = BeautifulSoup(driver.page_source, 'html.parser')	

			title = soup.find("div", class_="page-title").find("p").getText()
			print(title)

			description_list = soup.find("div", class_="field_item even", property="content:encoded").find_all("p")
			description = ""
			for des in description_list:
				description += des.getText()

			print(description)

			dates_list = soup.find_all("span", class_="ticket-dates ")
			for date in dates_list:
				print(date.getText())

			Krannert_address = "500 S Goodwin Ave, Urbana, IL 61801"
			print(Krannert_address)
			
			#the price part is a little too complex, and the type part is almost impossible. I will upload it tomorrow
			price = 0
			price_section = soup.find("div", class_="field_item even")
			if(price_section.find_all("span", class_="hover-item") is None):
				price = 0
			print(price)

			
			
		driver.get(url)
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		nextLink = soup.find("li", class_="date-next").find("a")[href]

		driver.get(nextLink)
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		if(soup.find_all("span", class_="event-details") is None):
			break
		else:
			url = nextLink
			continue
