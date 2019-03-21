
from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-twins.csv'
dateFormat = '%Y-%m-%d'
numDays = 30
linkCheckUrl = "https://www.instantseats.com/"

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)


UTFcounter = 0

genre = "Jazz & Blues"  
venuelink = "http://www.twinsjazz.com/"
venuename = "Twins Jazz"
addressurl = "https://goo.gl/maps/cs58EnKHujN2"
venueaddress = "1344 U St. NW, Washington, DC 20009"
musicurl = ""
doors = " "

localList = scraperLibrary.getLocalList()

fileName = '../scraped/scraped-twins.csv'
backupFileName = '../scraped/BackupFiles/TwinsScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


html = urlopen("http://www.instantseats.com/index.cfm?fuseaction=home.venue&venueid=10")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(index\.cfm\?fuseaction\=home\.event)")): #The link to each unique event page begins with "index.cfm?fuseaction=home.event"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "https://www.instantseats.com/" + newPage
        artistweb = newhtml # artist website almost never listed
        ticketweb = newhtml # event page is best ticket page
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        datelong = bsObj.find("span", {"class":"start-time"}).get_text()  # This pulls day of week, date, start time, & price.
        dateonly = re.findall(",\s([a-zA-Z]+\s[0-9]+)", datelong)[0] #Get date
        year = today.year
        date = datetime.datetime.strptime((dateonly.strip() + ' ' + str(year)), '%B %d %Y').date() 
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
            date = datetime.datetime.strptime((dateonly.strip() + ' ' + str(year + 1)), '%B %d %Y').date()
        if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        starttime = str(int(re.findall("[\n\r]([0-9]+)", datelong)[0])+12)+":00" #This extracts the number portion of the time, converts it to an integer, adds 12 ('cuz all Twins events in eve), converts to a string, and adds :00.
        if "free" in datelong.lower():
            price = 0
        else:
            price = re.findall("\$[0-9]+", datelong)[0]  #This extracts the ticket price
        artistname = bsObj.find("h2", {"class":"artist-name"}).get_text() #This gets the artist's name
        if len(re.findall('[A-Z]',artistname)) > 6 and len(re.findall('[A-Z]',artistname)) >= len(artistname)/2: #if CAPS are abused...
            artist = scraperLibrary.titleCase(artistname)
        else:
            artist = artistname
        if scraperLibrary.compactWord(artist) in localList:
            local = "Yes"
        else:
            local = ""
        descriptionparagraphs = list(bsObj.find("p", {"class":"description"}).next_siblings) # Gets the description.  NOTE 1 - be wary of multiple paragraphs with class of "Description"!!!!  NOTE 2 - funky paragraph structure required accessing the siblings rather than getting the description directly.
        description = ""
        counter = 0 
        while (counter < len(descriptionparagraphs)):
            try: #The content (or lack thereof) of some paragraphs cause fatal errors
                textblob = descriptionparagraphs[counter].get_text().strip()
                counter += 1
                if "$" in textblob and "cover" in textblob:
                    continue
                description += textblob + " \u00A4 "  # Description may be split between multiple paragraphs.  A symbol is concatenated in case, say, the site lists each musician in a separate paragraph.
            except:
                counter += 1
        description = re.sub('\s+',' ',description)
        description = description.replace(" \u00A4 \u00A4 "," \u00A4 ")
        description = description.strip().strip("\u00A4").strip() # eliminate trailing separators

        [description, readmore] = scraperLibrary.descriptionTrim(description, ["Visit Website"], 800, artistweb, newhtml)

        alldalinks = bsObj.findAll("a")
        musicurl = ""
        for onelink in alldalinks:
            try:
                if "youtube" in onelink.attrs["href"]:
                    musicurl = onelink.attrs["href"]
                    break
            except:
                continue
        artistpic = ""
        alldapics = bsObj.findAll("img")
        if starttime != "22:00" and starttime != "23:00":  #Pulls photo from site IF not the late show (only want pics for one show per day)
            for onepic in alldapics:
                if ".jpg" in onepic.attrs["src"]:
                    artistpic = "https://www.instantseats.com" + onepic.attrs["src"]
                    break

        write1 = (date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb)
        write2 = (date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
        write3 = (date, genre, artistpic, local, doors, price, starttime, artistweb, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
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
        pages.add(newPage)
        pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
csvFile.close()
backupCSV.close()

fileName = '../scraped/usedlinks-twins.csv'
backupFileName = '../scraped/BackupFiles/TwinsUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")