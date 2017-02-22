from bs4 import BeautifulSoup
import urllib.request

#start = 'https://www.eventbrite.com/d/il--champaign/events/'
#total_pages = soup.find("ul", class_="pagination__navigation-group").find("li", class_="js-page-link js-last-page show-large")#.find("a").text.strip()

url = 'https://www.eventbrite.com/d/il--champaign/events/?page={}' 
total_pages = 5
index = 1
for page in range(1, (total_pages+1)):
	with urllib.request.urlopen(url.format(page)) as response:
   		html = response.read()
	soup = BeautifulSoup(html, 'html.parser')

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
