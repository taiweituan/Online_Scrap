from bs4 import BeautifulSoup
import requests
import math
import threading
from functools import wraps
import time
import string
import csv
from validate_cust import ckCust

# get the total result count
def getPageCount(pageInfoSoup, resultsPerPage):
	resultsCnt = pageInfoSoup.find('div',{'class':'pagination'})
	if resultsCnt != None:
		resultsCnt = resultsCnt.p
		resultsCnt = str(resultsCnt.find_all(text=True)[1])
		resultsCnt = resultsCnt.split(' ')[-1]

		# get total pages for the search result
		totalPage = math.ceil(int(resultsCnt) / resultsPerPage)+1

		print 'Showing %s results per page'%resultsPerPage

		return totalPage
	else:
		return 0
		

# loop through all cities in csv file
def yellowPageScraper(writer, reader, counter, limit):
	searchCounter = 0
	for record in reader:
		searchCounter += 1
		
		if counter > 0:
			print 'Skipping city: %s, %s'%(record[0],record[1])
			print 'counter %s, limit: %s '%(counter, limit)
			counter-=1
			continue
		elif limit > 0:
			limit-=1
		
			# initialization 
			resultsPerPage = 30
			targetCity = '%s, %s'%(record[0],record[1])
			waitTime = 60

			# get page info
			r  = requests.get("http://www.yellowpages.com/search?search_terms=cctv&geo_location_terms=%s"%(targetCity))

			pageInfoData = r.text
			pageNumInfoSoup = BeautifulSoup(pageInfoData, "html.parser")

			# get number of the pages
			pageLength = int(getPageCount(pageNumInfoSoup, resultsPerPage))
			print ''
			print "Total Page: %s"%pageLength
			print '%s cities left to search'%(str(limit))
			print 'Searching city: %s'%targetCity

			# get information from all pages of current targeted city
			for currentPage in range(1, pageLength+1):
				q  = requests.get("http://www.yellowpages.com/search?search_terms=cctv&geo_location_terms=%s&page=%s"%(targetCity, currentPage))

				pageInfoData = q.text
				pageInfoSoup = BeautifulSoup(pageInfoData, "html.parser")

				print ''
				print 'Searching Page: %s / %s @%s'%(currentPage, pageLength, targetCity)
				print 'Scrap starts in %s second(s)'%waitTime
				print ''
				# take it slow
				time.sleep(waitTime)

				sectionDiv = pageInfoSoup.find_all('div',{'class':'srp-listing'})
				companyName = ''
				phoneNum = ''
				companyWebUrl = ''

				# get all records in current page
				for i in range(0,len(sectionDiv)-1):
					tempSoup = BeautifulSoup(str(sectionDiv[i]),'html.parser')

					# Get company Name
					companyName = tempSoup.find('a',{'class':'business-name'})
					companyName = ''.join(companyName.find_all(text=True))

					# get company address
					streetName = tempSoup.find('span',{'class':'street-address'})
					cityName = tempSoup.find('span',{'class':'locality'})
					stateName = tempSoup.find('span',{'itemprop':'addressRegion'})
					zipCode = tempSoup.find('span',{'itemprop':'postalCode'})

					if streetName != None and stateName != None and zipCode != None and phoneNum != None:
						streetName = ''.join(streetName)
						cityName = ''.join(cityName)
						stateName = ''.join(stateName)
						zipCode = ''.join(zipCode)
					else:
						streetName = 	'Not Provided'
						cityName = 		'Not Provided'
						stateName = 	'Not Provided'
						zipCode = 		'Not Provided'
						
					# get company phone number
					phoneNum = tempSoup.find('div',{'itemprop':'telephone'})
					if phoneNum != None:							
						phoneNum = ''.join(phoneNum.find_all(text=True))
						phoneNum = phoneNum.replace('-','')
					else:
						phoneNum = 'Phone Not Porvided'

					#get company website URL
					companyWebUrl = tempSoup.find('a',{'class':'track-visit-website'})
					if companyWebUrl != None:
						companyWebUrl = companyWebUrl['href']
					else: 
						companyWebUrl = 'No Website Exist'

					# Check if the customer is currently our customer
					currentCustomer = ckCust(companyName, phoneNum)

					if currentCustomer == False:
						finalResult = []
						finalResult.extend([companyName, phoneNum, companyWebUrl, streetName, cityName,stateName,zipCode])
						writer.writerows([finalResult])
						print finalResult
					else: 
						print "'%s' is current customer, skipped"%(companyName)
		
		else: 
			print ''
			print 'Search ended at: %s'%searchCounter
			break


# Main()
readdir = 'C:\\Users\\taiwei\\Desktop\\YelpStuff\\CityList.csv'
writedir = 'C:\\Users\\taiwei\\Desktop\\YellowPageScrap.csv'
with open(readdir, 'rb') as read_file:
	with open(writedir, 'wb')as write_file:
		writer = csv.writer(write_file, delimiter=',')
		reader = csv.reader(read_file)
		skipCounter = int(raw_input('How many cities to skip: '))
		scrapLimit = int(raw_input('How many cities to search: '))

		yellowPageScraper(writer,reader, skipCounter, scrapLimit)
		print 'Scrap has ended'
		print ''