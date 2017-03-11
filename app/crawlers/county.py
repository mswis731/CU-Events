#from app import app, mysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
import re

def crawl():
  connection = mysql.get_db()
  cursor = connection.cursor()

  urls = ["http://www.visitchampaigncounty.org/events/category/14/arts-and-theater", "http://www.visitchampaigncounty.org/events/category/22/exhibits", "http://www.visitchampaigncounty.org/events/category/21/family---friendly", "http://www.visitchampaigncounty.org/events/category/16/festivals-and-fairs", "http://www.visitchampaigncounty.org/events/category/71/food-and-drink"] 
  driver = webdriver.PhantomJS()
  
  for url in urls:
    driver.get(url)
    #WebDriverWait(driver, 10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #events = soup.find_all("div", class_="col-sm-2")
    #print(len(events))

    lists = soup.find_all("div", class_="event-detail-box")
    for list_ in lists:
      title = list_.find("a").contents[0]
      print(title)
      event_urls = list_.find("a")["href"]  
      print("http://www.visitchampaigncounty.org/" + event_urls)
      driver.get("http://www.visitchampaigncounty.org/" + event_urls)
      event_soup = BeautifulSoup(driver.page_source, "html.parser")
      #print(event_soup.find("h4"))
      location_general = event_soup.find("li", class_="box place border-right").getText() 
      print (location_general)

      time_general = event_soup.find("li", class_="box date border-right").getText()
      print(time_general)

      price_general =  event_soup.find("li", class_="box tickte border-right").getText()
      print (price_general)
if __name__ == "__main__":
  crawl()
