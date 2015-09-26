from bs4 import BeautifulSoup
import requests
import math
import threading
from functools import wraps
import time
import string
import csv
#from validate_cust import ckCust

#readdir = 'P:\\WebTeam\\Documents\\US-MajorCities.csv'
readdir = 'C:\\WEBSITES\\STORAGE\\YelpStuff\\CityList.csv'
writedir = 'C:\\WEBSITES\\STORAGE\\YelpStuff\\YelpScrap_Out.csv'
with open(readdir, 'rb') as read_file:
	with open(writedir, 'wb')as write_file:
		writer = csv.writer(write_file, delimiter=',')
		reader = csv.reader(read_file)
		
		

		# loop through all major cities
		for record in reader:
			listPerPage = 10
			targetZipcode = '%s, %s'%(record[0],record[1])

			print 'Searching City: %s'%(targetZipcode)

			q  = requests.get("http://www.yelp.com/search?find_desc=cctv&find_loc=%s&start=0"%(targetZipcode))
			data1 = q.text
			soup1 = BeautifulSoup(data1, "html.parser")

			# get total result counts
			wantedStuffName = soup1.find('span', class_="pagination-results-window")
			wantedStuffName = ''.join(wantedStuffName.find_all(text=True))
			wantedStuffName = wantedStuffName.replace(' ', '')
			resultCount = int(wantedStuffName.split('of',1)[1])
			
			print 'Total result of this city:', resultCount

			# calculate total pages
			totalPages = math.ceil(resultCount/listPerPage)+1

			print 'Total Pages:', totalPages

			# loop through all pages to scrap info
			for currentPage in range(0, int(totalPages)):
				startFrom = currentPage * 10
				#r  = requests.get("http://www.yelp.com/search?find_desc=cctv&find_loc=%s&start=%s" %('Los Angeles, CA','330'))
				
				r  = requests.get("http://www.yelp.com/search?find_desc=cctv&find_loc=%s&start=%s" %(targetZipcode,str(startFrom)))

				print 'waiting for 20 secs before loading...'
				time.sleep(20)
				data = r.text
				
				print ''
				print "Start from: %s" %str(startFrom)
				print ''
				#print data
				soup = BeautifulSoup(data, "html.parser")

				wantedStuffName = soup.find_all('a', class_="biz-name")
				wantedStuffPhoneNum = soup.find_all('span',class_="biz-phone")
				#wantedStuffHref = soup.find_all('a',{'class':'biz-name'} )[0]['href']
				extractedName = ''
				extractedPhone = ''

				# read results in the page
				for i in range(1,len(wantedStuffName)):
					wantedStuffHref = soup.find_all('a',{'class':'biz-name'} )[i]['href']

					# name sometimes contain invalid characters, ignore all of them
					extractedName = "".join(wantedStuffName[i].find_all(text=True))
					extractedName = extractedName.encode('ascii','ignore')

					# extract phone number to correct format
					extractedPhone = "".join(wantedStuffPhoneNum[i].find_all(text=True))
					extractedPhone = str(extractedPhone[-19:-5])
					extractedPhone= extractedPhone.replace('-', '')

					# make simplified url to full url
					extractedHref = "http://www.yelp.com%s" %(wantedStuffHref)
					
					# set idle time before loading page.(in case of ban)
					print 'waiting for 30 secs before loading...'
					time.sleep(30)
					
					# load each company's page
					s = requests.get(extractedHref)
					data2 = s.text
					soup2 = BeautifulSoup(data2, "html.parser")

					# get web address
					webAddress = soup2.find('div',{'class':'biz-website'})
					
					if webAddress != None:
						webAddress = webAddress.find('a').text
						webAddress = webAddress.encode('ascii', 'ignore')
						webAddress = str(webAddress)

					else:
						webAddress = 'No Website'

					# get location address
					streetAddress = soup2.find('span',{'itemprop':'streetAddress'})
					cityName = soup2.find('span',{'itemprop':'addressLocality'})
					stateName = soup2.find('span',{'itemprop':'addressRegion'})
					zipCode = soup2.find('span',{'itemprop':'postalCode'})
					
	# get full address
					if streetAddress != None:
						streetAddress = str(''.join(streetAddress.find_all(text=True)))
						if cityName != None:
							cityName = str(''.join(cityName.find_all(text=True)))
						else:
							cityName = ''

						if stateName != None:
							stateName = str(''.join(stateName.find_all(text=True)))
						else:
							stateName  = ''
						
						if zipCode != None:
							zipCode = str(''.join(zipCode.find_all(text=True)))
						else:
							zipCode = ''
						#fullAddress = "%s, %s, %s, %s"%(streetAddress, cityName, stateName, zipCode)
					else:	
						#fullAddress = 'Not provided'
						streetAddress = 'N/A'
						cityName = 'N/A'
						stateName = 'N/A'
						zipCode= 'N/A'
					
					# black list
					blackList = ['At&t','Comcast','xfinity','Verison','LT SECURITY','lt security']
					isBlackList = False
					
					# store name contains black list
					for j in range(0,len(blackList)):
						if blackList[j] in extractedName:
							isBlackList = True
					
					# whether is company a current customer
					#currentCustomer = ckCust(extractedName, extractedPhone)

					# print final result and put them in .csv file
					if isBlackList == False:
						finalResult = []
						finalResult.extend([extractedName, extractedPhone, webAddress, streetAddress,cityName,stateName,zipCode])
						writer.writerows([finalResult])
						print finalResult
					else: 
						print "'%s' is current customer, skipped"%(extractedName)

	