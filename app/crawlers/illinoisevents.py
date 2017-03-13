from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
import urllib.request 

class eventData:
    title = ""
    eventType = ""
    location = ""
    startDate = ""
    endDate = ""
    startTime = "00:00:00"
    endTime = "00:00:00"
    cost = ""

    def __init__(self,title="", eventType="", location="", startDate="", startTime = "00:00:00", endTime = "00:00:00", endDate= "", cost=""):
        self.title = title
        self.eventType = eventType
        self.location = location
        self.startDate = startDate
        self.endDate = startDate
        self.startTime = startTime
        self.endTime = endTime
        self.cost = cost

def printObject(event):
	print("title: " + event.title + "\n" + "event type: " + event.eventType + "\n" + "location: " + event.location + "\n" + "start date: " + event.startDate)
	print("end date: " + event.endDate + "\n" + "start time: " + event.startTime + "\n" + "end time: " + event.endTime + "\n"  "cost: " + event.cost + "\n")

def processDate(event):
	date = event.startDate
	if ("-" in date and (date.find("-") < date.rfind("2017"))) or date.count("-") > 1:
		index = date.find("-")
		index2 = date.rfind("2017")+7
		event.startDate = date[0:index-1]
		if(index2 > len(date)):
			event.endDate = date[index+2:]
		else:
			event.endDate = date[index+2:index2-3]
			index3 = date.rfind("-")
			if(index3 == index):
				event.startTime = date[index2:]
				event.endTime = event.startTime
			else:
				event.startTime = date[index2:index3]
				event.endTime = date[index3+2:]
	else:
		index = date.find("2017")+3
		indexAm = date.find("am")
		indexPm = date.find("pm")
		event.startDate = date[0:index+1]
		event.endDate = event.startDate
		if(indexAm != -1 or indexPm != -1):
			index3 = date.rfind("-")
			index4 = index+4
			if(index3 == -1):
				event.startTime = date[index4:]
				event.endTime = event.startTime
			else:
				event.startTime = date[index4:index3]
				event.endTime = date[index3+2:]







baseUrl = 'https://illinois.edu'
start = 'https://illinois.edu/calendar/list/7?pos=0'
#connection = mysql.get_db()
#cursor = connection.cursor()
page = urllib.request.urlopen(start) 
soup = BeautifulSoup(page, 'html.parser')

eventList = []
urlDict = {}
soup.prettify()
eventCounter = 0
i = 0
for anchor in soup.find_all('a', href=True):
	if "eventId" in anchor['href'] and baseUrl+anchor['href'] not in urlDict:
		urlDict.update({baseUrl+anchor['href']: 0})
		print(baseUrl+anchor['href'])
		eventpage =  urllib.request.urlopen(baseUrl+anchor['href'])
		innersoup = BeautifulSoup(eventpage, 'html.parser')
		eventD = eventData()
		innersoup.prettify()
		eventD.title = innersoup.find_all('h2')[0].text
		eType = innersoup.find('dt', text='Event Type')
		eventD.eventType = eType.find_next_sibling('dd').text.strip()
		eLoc = innersoup.find('dt', text='Location')
		if(eLoc is not None):
			eventD.location = eLoc.find_next_sibling('dd').text.strip()
		eDate = innersoup.find('dt', text='Date ')
		eventD.startDate = eDate.find_next_sibling('dd').text.strip()
		eCost = innersoup.find('dt', text='Cost')
		if(eCost is not None):
			eventD.cost = eCost.find_next_sibling('dd').text.strip()
		eventList.append(eventD)
		i += 1
		if(i == 20):
			break

for event in eventList:
	processDate(event)
	printObject(event)


