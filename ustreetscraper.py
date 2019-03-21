#Scrapes U Street Music Hall events, using - http://www.ustreetmusichall.com/calendar/  

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-ustreet.csv'
dateFormat = '%Y-%m-%d'
numDays = 30
linkCheckUrl = True

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)

UTFcounter = 0 # Counter for number of encoding problems

local = "" 
doors = " "
genre = "Rock & Pop" 
artistpic = ""
ulink = "http://www.ustreetmusichall.com/"
uname = "U Street Music Hall"
umap = "https://goo.gl/maps/S5PQVPXGySK2"
uaddress = "1115 U St NW, Washington, DC 20009"
tigerslink = "http://www.tentigersdc.com/"
tigersname = "Ten Tigers"
tigersmap = "https://goo.gl/maps/QmFCBGtQVxn"
tigersaddress = "3813 Georgia Ave NW, Washington, DC 20011"

fileName = '../scraped/scraped-ustreet.csv'
backupFileName = '../scraped/BackupFiles/UStreetScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


html = urlopen("http://www.ustreetmusichall.com/calendar/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "http://www.ustreetmusichall.com" + newPage
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        dadate = bsObj.find("h2", {"class":"dates"}).get_text().strip() 
        year = today.year
        try:
            date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%B %d %Y').date()
        except:
            try:
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%A %B %d %Y').date()
            except:
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%A %b %d %Y').date()
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
            try:
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%B %d %Y').date()
            except:
                try:
                    date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%A %B %d %Y').date()
                except:
                    date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%A %b %d %Y').date()
        if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        starttime = bsObj.find("span", {"class":"start"}).get_text() # Pulls time, including pm
        starttime = starttime.replace("Show:", "").strip() # U Street has been adding 'Show:' text to time field of late...
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range
        except:   #Crashed with free event; woulda crashed w/ TBA event...
            try:
                price = bsObj.find("h3", {"class":"free"}).get_text().strip()  # Free event(s) actually have the price listed in an h3 w/ a class of 'free'
            except:
                print("Skipped",newPage,date,"because could not find price")
                continue
        artist = bsObj.find("h1", {"class":"headliners summary"}).get_text() # Event / top artist name
        artist = re.sub('[\[\(][Oo][Pp][Ee][Nn][\s\-][Tt][Oo][\s\-][Cc][Ll][Oo][Ss][Ee][\]\)]','',artist)
        if "at 9:30 Club" in artist or "Union Stage" in artist or "cancelled" in artist.lower():
            continue
        if "Ten Tigers" in artist:
            venuelink = tigerslink
            venuename = tigersname
            addressurl = tigersmap
            venueaddress = tigersaddress
            artist = re.sub('\([aA]t\sTen\sTigers\)','',artist)
        else:
            venuelink = ulink
            venuename = uname
            addressurl = umap
            venueaddress = uaddress
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]
        except:
            artistweb = newhtml
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"bio"}).get_text() # Get the description, which does include a lot of breaks - will it be a mess?
        except:
            description = ""

        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 700, artistweb, newhtml) #U Street gets shorter descriptions

        musicurl = ""
        try:
            musicurl = bsObj.find("li", {"class":"soundcloud"}).find("a").attrs["href"]
        except:
            try:
                iframes = bsObj.findAll("iframe") # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
                for onei in iframes:  
                    if "youtube" in onei.attrs["src"]:
                        musicurl = onei.attrs["src"]
                        break  # Once first video is found, move along (don't take back-up band's video over headliner; don't have 'else' overwrite found link)
                    else:
                        if "soundcloud" in onei.attrs["src"]:
                            musicurl = onei.attrs["src"]
                            break  # If first iframe has soundcloud link, grab it and move along
                        else:
                            musicurl = ""  # In case there are iframes, but no videos
            except:
                musicurl = ""
        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door
        except:
            ticketweb = ""
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

fileName = '../scraped/usedlinks-ustreet.csv'
backupFileName = '../scraped/BackupFiles/UStreetUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")
