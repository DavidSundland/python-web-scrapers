#Scrapes Hill Country BBQ's events, using - http://hillcountry.com/dc/music-calendar/ 

import requests #urllib didn't work with this site for some reason
from urllib.request import urlopen #for pulling info from websites (will not be used if Error 403 encountered)
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-hillcountry.csv'
dateFormat = '%Y-%m-%d'
numDays = 30
linkCheckUrl = ''
genre = "Americana"

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)

doors = " "
venuelink = "https://hillcountry.com/dc/"
venuename = "Hill Country BBQ"
addressurl = "https://goo.gl/maps/LN9RTL9vZiS2"
venueaddress = "410 7th St. NW, Washington, DC 20004"

UTFcounter = 0 # Counter for number of encoding problems

fileName = '../scraped/scraped-hillcountry.csv'
backupFileName = '../scraped/BackupFiles/HillCountryScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)

# for pointer in range(1,4):  #events are spread over multiple pages
#    if pointer == 1:
#        page = "https://hillcountry.com/dc/music-calendar/"
#    else:
#        page = "https://hillcountry.com/dc/music-calendar/" + str(pointer) + "/"

page = "https://www.ticketfly.com/venue/1281-hill-country-dc/"
try:
    html = urlopen(page)
    bsObj = BeautifulSoup(html)
except:
    url = page
    bsObj = BeautifulSoup(requests.get(url).text)

for event in bsObj.findAll("abbr", {"class":"url"}): 
    newPage = event.attrs["title"] #title matches link text
    if newPage not in pages: #A new link has been found
#        counter += 1
        print("found a link:",newPage)
        newhtml = newPage
        try:
            html = urlopen(newhtml)
            bsObj = BeautifulSoup(html)
        except:
            bsObj = BeautifulSoup(requests.get(newhtml).text)
        datelong = bsObj.find("title").get_text()
        date = re.findall("[JFMASOND][a-z]+\s[0-9]{1,2}[snrt][tdh]\,\s20[12][0-9]", datelong)[0]
        date = re.sub('st|nd|rd|th','',date)
        dadate = datetime.datetime.strptime((date.strip()), '%B %d, %Y')
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        artist = bsObj.find("h1", {"class":"headliners"}).get_text()
        if "SOLD OUT" in artist.upper() or "CLUB CLOSED" in artist.upper() or "PRIVATE EVENT" in artist.upper():
           continue
        localList = scraperLibrary.getLocalList()
        if scraperLibrary.compactWord(artist) in localList:
            local = "Yes"
        else:
            local = ""
        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"] 
        except:
            ticketweb = ""
        try:
            price = bsObj.find("p", {"class":"event-tickets-price"}).get_text()
        except:
            print("found no price; free?")
            price = "No cover"
        timelong = bsObj.find("span", {"class":"start"}).get_text()
        starttime = re.findall("[0-9]{1,2}\:[0-9]{1,2}\s*[pPaA][mM]",timelong)[0]
        if starttime == '8:30AM' and 'karaoke' in artist.lower():
            starttime = '8:30PM'  #some recurring events have a typo (da karaoke ain't in the morning)
        try:
            artistweb = bsObj.find("li", {"class":"external-links-site"}).find("a").attrs["href"] 
        except:
            try:
                artistweb = bsObj.find("li", {"class":"external-links-facebook"}).find("a").attrs["href"] 
            except:
                artistweb = ""
        description = ""
        bands = bsObj.findAll("p", {"class":"description"})
        for band in bands:
            description += band.get_text().strip() + " "
            if len(description) > 800:
                break
                
        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml) 
        
        try:
            musicurl = bsObj.find("a", {"class":"playlist-video"}).attrs["href"]
        except:
            musicurl = ""
        
        try:
            artistpic = bsObj.find("video").attrs["poster"]
        except:
            try:
                artistpic = bsObj.find("div", {"id":"artist-image"}).find("img").attrs["src"]
            except:
                artistpic = ""
           
        write1 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb)
        write2 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
        write3 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
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

fileName = '../scraped/usedlinks-hillcountry.csv'
backupFileName = '../scraped/BackupFiles/HillCountryUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")
