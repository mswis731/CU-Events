#from app import app, mysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
import re

def crawl():
  #connection = mysql.get_db()
  #cursor = connection.cursor()

  url = "http://eventful.com/champaign/events?q=*&ga_search=*&sort_order=Date&ga_type=events&within=5&units=mi"	
  driver = webdriver.PhantomJS()
  
  while 1:
    driver.get(url)
    WebDriverWait(driver, 10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    events = soup.find_all("div", class_="col-sm-2")
    print(len(events))

"""
		events = soup.findAll("div", class_="event-box")
		for event in events:

			title = soup.find("div", class_ = "event-detail-box").find("h3").find("a")["href"].text.strip()

			event_url = event.find("div", class_="event-box").find("div", class_="event-detail-box").find("h3").find("a")["href"]
			driver.get(event_url)
			event_soup = BeautifulSoup(driver.page_source, 'html.parser')

			location_general = event_soup.find("li", class_ = "box place border-right")

			location_all = location_general.getText()

			#stardate_general=event_soup

			print("Title: {}".format(title))
			print("Location {}".format(location_all))
"""

if __name__ == "__main__":
  crawl()
