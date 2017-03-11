import sys
#goes back two levels so that we can import app 
sys.path.append('../../')

from app import app, mysql
from app.crawlers.mappings import map_months, map_times, map_categories, map_event_types
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
import re

def crawl():
  #connection = mysql.get_db()
  #cursor = connection.cursor()

  urls = ["http://www.visitchampaigncounty.org/events/category/14/arts-and-theater", "http://www.visitchampaigncounty.org/events/category/22/exhibits", "http://www.visitchampaigncounty.org/events/category/21/family---friendly", "http://www.visitchampaigncounty.org/events/category/16/festivals-and-fairs", "http://www.visitchampaigncounty.org/events/category/71/food-and-drink", "http://www.visitchampaigncounty.org/events/category/19/history-and-education", "http://www.visitchampaigncounty.org/events/category/15/music", "http://www.visitchampaigncounty.org/events/category/17/nature-and-outdoors", "http://www.visitchampaigncounty.org/events/category/18/sports"] 
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

      print(building)
      print(addrAndStreet)
      print(city)
      print(zipcode + '\n')

      time_general = event_soup.find("li", class_="box date border-right").getText()
      #print((time_general).split('\n'))
      year = time_general.split('\n')[2].split(" ")[3]
      month =time_general.split('\n')[2].split(" ")[1]
      
      month = map_months[month]
      # if month == 'March':
      #   month = '03'
      # if month == 'April':
      #   month = '04'

      date = time_general.split('\n')[2].split(" ")[2][:-1]

      full_date = "{}-{}-{}".format(year, month, date) 
      #print(full_date)
  
      start_time = "00:00:00"
      end_time = "00:00:00"
      end_t = end_time
      start_t = start_time
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

      low_price = 0;
      high_price = 0;
      price_general =  event_soup.find("li", class_="box tickte border-right").getText()
      print (price_general)
      price_split = (price_general.split('\n'))[2]
      if 'Buy Tickets' in price_split:
        ticket_url = event_soup.find("li", class_="box tickte border-right").find("span", class_="site-link").find("a")["href"]
        print(ticket_url)
         
      if (url == "http://www.visitchampaigncounty.org/events/category/22/exhibits") or (url == "http://www.visitchampaigncounty.org/events/category/16/festivals-and-fairs"):
        event_type = map_event_types[url]
        print (event_type)
      else:
        category = map_categories[url]
        print (category)

      #fix description to get rid of including unneccesary css properties 
      description =  event_soup.find("div", class_="panel-body").getText()
      print(description)

if __name__ == "__main__":
  crawl()
