#Scrapes Mr. Henry's events, using - http://www.mrhenrysdc.com/calendar/2019-04/ 


from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #regular expressions
import csv #comma-separated values
import datetime
from datetime import date # necessary for properly calculating time differences in months
from dateutil.relativedelta import relativedelta # necessary for properly calculating time differences in months

import scraperLibrary #custom library for venue site scraping
import scraperLibraryOOP # Object-Oriented versions of most scraperLibrary functions

class Scraped: # move to scraperLibraryOOP when scraper completed and tested
    def __init__(self, date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb, artisturl):
        self.date = date
        self.genre = genre
        self.artistpic = artistpic
        self.local = local
        self.doors = doors
        self.price = price
        self.starttime = starttime
        self.newhtml = newhtml
        self.artist = artist
        self.venuelink = venuelink
        self.venuename = venuename
        self.addressurl = addressurl
        self.venueaddress = venueaddress
        self.description = description
        self.readmore = readmore
        self.musicurl = musicurl
        self.ticketweb = ticketweb
        self.artisturl = artisturl

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

#Note - at present, 1 object is created, and it is mutated for every event. While this will work (and fits with older, non-OOP scrapers), a better, more OOPy approach may be to have 1 array of objects or 1 object containing separate objects for each event...
mrHenrys = Scraped("", "Jazz&Blues", "", "", " ", "", [], "", "", "http://www.mrhenrysdc.com/", "Mr. Henry's", "https://goo.gl/maps/D8WAijc1bi92", "601 Pennsylvania Ave. SE, Washington, DC 20007", "", "", "", "", "")

usedLinksFile = '../scraped/usedlinks-mrhenrys.csv'
dateFormat = '%Y-%m-%d'
numDays = 30
linkCheckUrl = ''

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)
UTFcounter = 0 # Counter for number of encoding problems

fileName = '../scraped/scraped-mrhenrys.csv'
backupFileName = '../scraped/BackupFiles/MrHenrysScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


# Scraping 1 month at a time, creating URL to match: http://www.mrhenrysdc.com/calendar/2019-05/
for monthrange in range(0,2):  # look at this month & next; possibly look farther in future
    month = ((today+relativedelta(months=+monthrange)).strftime("%m"))
    monthurl = "http://www.mrhenrysdc.com/calendar/" + (today+relativedelta(months=+monthrange)).strftime("%Y") + "-" + month + "/"
    html = urlopen(monthurl)
    bsObj = BeautifulSoup(html)
    for link in bsObj.findAll("a", {"class":"url"}):
        newPage = link.attrs["href"] #extract the links
        if newPage not in pages: #A new link has been found
            pages.add(newPage)
            if "lipstick" in newPage or "boardgame" in newPage or "cheers-capitol" in newPage or "dining-out" in newPage or "trivia" in newPage: #Recurring non-music events
                continue
            mrHenrys.newhtml = newPage
            html = urlopen(mrHenrys.newhtml)
            print(newPage)
            bsObj = BeautifulSoup(html)
            mrHenrys.date = bsObj.find("abbr", {"class":"tribe-events-start-date"}).attrs["title"] #date in YYYY-MM-DD format
            if datetime.datetime.strptime(mrHenrys.date, '%Y-%m-%d').weekday() == 3:
                mrHenrys.genre = "Americana"  #Mr. Henry's almost always has Americana on Thursdays...
            pageanddate.add((newPage,mrHenrys.date,datetoday))  # Add link to list, paired with event date and today's date
            mrHenrys.artist = bsObj.find("h1", {"class":"tribe-events-single-event-title"}).get_text().strip()
            if mrHenrys.artist == "Smith Jackson":
                mrHenrys.artist = "SmithJackson"
            mrHenrys.artist = mrHenrys.artist.replace("Double Header","")
            localList = scraperLibrary.getLocalList()
            if scraperLibrary.compactWord(mrHenrys.artist) in localList:
                mrHenrys.local = "Yes"
            else:
                mrHenrys.local = ""

            longtime = bsObj.find("span", {"class":"tribe-event-date-start"}).get_text().strip()
            starttime = re.findall("[0-9]{1,2}\:[0-5][0-9]\s[aApP][mM]",longtime)[0]
            if starttime == "6:00 pm":  # events with 6:00 start time actually have 6:00 doors but 2 different event times
                mrHenrys.starttime = ["7:30 pm", "9:45 pm"]
            else:
                mrHenrys.starttime = [starttime]
            try: # Most events are free, but 1 or 2 events a month require tickets
                mrHenrys.price = bsObj.find("span", {"class":"tribe-events-cost"}).get_text().strip()
                links = bsObj.findAll("a")
                for link in links:
                    if "brownpaper" in link.attrs["href"] or "bpt" in link.attrs["href"]:
                        mrHenrys.ticketweb = link.attrs["href"]
                        break
                    else:
                        mrHenrys.ticketweb = ""
            except:
                mrHenrys.price = 0
                mrHenrys.ticketweb = ""

            mrHenrys.description = bsObj.find("div", {"class":"tribe-events-single-event-description"}).get_text().strip()
                
            # [description, readmore] = 
            scraperLibraryOOP.descriptionTrim(mrHenrys,[], 800)
            
            if "doubleheader" in mrHenrys.artist.lower().replace(' ','') and "by&by" in mrHenrys.description.lower().replace(' ','') and "moosejaw" in mrHenrys.description.lower().replace(' ','') and len(mrHenrys.description) < 200:
                mrHenrys.description = "Every 3rd Thursday of the Month, we are proud to present a Bluegrass double header, feature the bands By&By and Moosejaw.  By & By, 'your friendly neighborhood bluegrass band,' brings to roots music — and original material in the bluegrass tradition — 'a powerful lead singer, mesmerizing harmonies, and instrumental arrangements tight enough to bounce a nickel on.'  Moose Jaw is Prince George’s County, Maryland’s premiere bluegrass ensemble. Organized as a cooperative, they performing traditional, not so traditional, original and not so original tunes for varying audiences throughout the mid-Atlantic region."
            
            if mrHenrys.artist == "Rose Moraes":
                mrHenrys.description = "Moraes has introduced thousands of music lovers to Brazilian music through performances in Switzerland, Poland, Brazil and the US, where she now resides. She has performed at Zinc Bar and The Iridium in New York City, for Artscape and the yearly sold-out Carnival concerts at Creative Alliance in Baltimore, and in countless Washington, D.C. venues and festivals such as D.C. Jazz Festival and Adams Morgan Day. She has two albums to her credit and collaborates on many musical projects."
            try:
                mrHenrys.artistpic = bsObj.find("div", {"class":"tribe-events-event-image"}).find("img").attrs["src"]
            except:
                mrHenrys.artistpic = ""
            
            for onetime in mrHenrys.starttime:
                write1 = (mrHenrys.date, mrHenrys.genre, mrHenrys.artistpic, mrHenrys.local, mrHenrys.doors, mrHenrys.price, onetime, mrHenrys.newhtml, mrHenrys.artist, mrHenrys.venuelink, mrHenrys.venuename, mrHenrys.addressurl, mrHenrys.venueaddress, mrHenrys.description, mrHenrys.readmore, mrHenrys.musicurl, mrHenrys.ticketweb)
                write2 = (mrHenrys.date, mrHenrys.genre, mrHenrys.artistpic, mrHenrys.local, mrHenrys.doors, mrHenrys.price, onetime, mrHenrys.newhtml, mrHenrys.artist, mrHenrys.venuelink, mrHenrys.venuename, mrHenrys.addressurl, mrHenrys.venueaddress, mrHenrys.description.encode('UTF-8'), mrHenrys.readmore, mrHenrys.musicurl, mrHenrys.ticketweb)
                write3 = (mrHenrys.date, mrHenrys.genre, mrHenrys.artistpic, mrHenrys.local, mrHenrys.doors, mrHenrys.price, onetime, mrHenrys.newhtml, mrHenrys.artist.encode('UTF-8'), mrHenrys.venuelink, mrHenrys.venuename, mrHenrys.addressurl, mrHenrys.venueaddress, mrHenrys.description.encode('UTF-8'), mrHenrys.readmore, mrHenrys.musicurl, mrHenrys.ticketweb)
                try:  # Might crash with weird characters.
                    writer.writerow(write1)
                    backupwriter.writerow(write1)
                except:
                    UTFcounter += 1
                    try:
                        writer.writerow(write2)
                        backupwriter.writerow(write2)
                        print("Using UTF encoding for description", date)
                    except:
                        writer.writerow(write3)
                        backupwriter.writerow(write3)
                        print("Using UTF encoding for artist and description", date)
csvFile.close()
backupCSV.close()

fileName = '../scraped/usedlinks-mrhenrys.csv'
backupFileName = '../scraped/BackupFiles/MrHenrysUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")
