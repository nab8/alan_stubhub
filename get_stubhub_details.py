# Importing some useful libraries
import json
import time
import pycurl
import os
# Create a config.py file in the same directory with a single line in this format.  Replace token with your actual token.
# api_key="token"
from config import api_key
cwd=os.getcwd()
from io import BytesIO
# Get the Website
buffer = BytesIO()
# Website goes here
website='https://api.stubhub.com/search/catalog/events/v3?q=%22Washington%20Huskies%22&sort=eventDateLocal&wt=json&fieldList=*,ticketInfo&rows=300'
c = pycurl.Curl()
c.setopt(c.FOLLOWLOCATION, True)
c.setopt(pycurl.SSL_VERIFYPEER, 0)   
c.setopt(pycurl.SSL_VERIFYHOST, 0)
c.setopt(c.HTTPHEADER, ['Authorization: Bearer '+api_key])
c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
c.setopt(c.URL, website)
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()
body = buffer.getvalue()
stubhub_json=body.decode('iso-8859-1')
# Convert the JSON into something useful
stubhub_parsed = json.loads(stubhub_json)
stubhub_events=stubhub_parsed['events']
print("Total events found: "+str(len(stubhub_events)))
# Printing the first line of the CSV and creating a new file using the w flag
for event in stubhub_events:
	try: event['performersCollection'][1]['name']
	except IndexError:
		doNothing = ""
	else:
		# Creating Event File Name in format stubhub_eventid_sport_date.csv
		filename_sport="NA"
		if 'Washington Huskies' in event['performersCollection'][0]['name']:
			filename_sport=event['performersCollection'][0]['name'].replace("Washington Huskies ","").replace(" ","_")
		elif 'Washington Huskies' in event['performersCollection'][1]['name']:
			filename_sport=event['performersCollection'][1]['name'].replace("Washington Huskies ","").replace(" ","_")
		filename_date="TBD"
		if 'T' in event['eventDateLocal']:
			filename_date=event['eventDateLocal'].split("T",1)[0]
		buffer2 = BytesIO()
		filename="stubhub_"+str(event['id'])+"_"+filename_sport+"_"+filename_date+".csv"
		# Get each ID
		website='https://api.stubhub.com/search/inventory/v2?eventid='+str(event['id'])+'&rows=1000'
		print("Checking "+website+" for "+filename_date+" "+filename_sport+" tickets")
		c = pycurl.Curl()
		c.setopt(c.FOLLOWLOCATION, True)
		c.setopt(pycurl.SSL_VERIFYPEER, 0)   
		c.setopt(pycurl.SSL_VERIFYHOST, 0)
		c.setopt(c.HTTPHEADER, ['Authorization: Bearer '+api_key])
		c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
		c.setopt(c.URL, website)
		c.setopt(c.WRITEDATA, buffer2)
		c.perform()
		c.close()
		body = buffer2.getvalue()
		# Body is a byte string.
		# We have to know the encoding in order to print it to a text file
		# such as standard output.
		details_json=body.decode('iso-8859-1')
		# Convert the JSON into something useful
		try: details_parsed = json.loads(details_json)
		except ValueError:
			print("No seats found, going to next event.")
		else:
			if 'listing' in details_parsed:
				stubhub_listings=details_parsed['listing']
				print("Seats found, saving file as ",cwd,"/",filename,sep="")
				print("Event Title,Event Date,Seat Section,Seat Row,Ticket Price,Ticket Quantity,Date Downloaded",sep="",file = open(filename,'a'))
				for listing in stubhub_listings:
						print("\"",event['name'],"\",",sep="",end="",file = open(filename,'a'))
						print("\""+event['eventDateLocal'],"\",",sep="",end="",file = open(filename,'a'))
						try:
								print(listing['sectionName'][listing['sectionName'].rindex(' ')+1:],",",sep="",end="",file = open(filename,'a'))
						except ValueError:
								print(",",sep="",end="",file = open(filename,'a'))
						print(listing['row'],",",sep="",end="",file = open(filename,'a'))
						print("$",listing['currentPrice']['amount'],",",sep="",end="",file = open(filename,'a'))
						print(listing['quantity'],",",sep="",end="",file = open(filename,'a'))
						print(time.strftime("%Y-%m-%d"),sep="",file = open(filename,'a'))
			time.sleep(8)
cwd=os.getcwd()