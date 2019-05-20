#Scrapes Pearl's events, using - https://www.unionstage.com/listing/
#DO, FUTURE - figure out system for genre and local...

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-union.csv'
dateFormat = '%m/%d/%Y'
numDays = 30
linkCheckUrl = 'https://www.unionstage.com'

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)


UTFcounter = 0

local = "" 
doors = " "
genre = "Rock & Pop"  # Add test for genre in future

localList = scraperLibrary.getLocalList()

fileName = '../scraped/scraped-union.csv'
backupFileName = '../scraped/BackupFiles/UnionScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


html = urlopen("https://www.unionstage.com/listing/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "https://www.unionstage.com" + newPage
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        datelongest = bsObj.find("span", {"class":"value-title"}).attrs["title"] 
        datelonger = re.findall("20[12][0-9]\-[0-2][0-9]\-[0-3][0-9]T[0-9]{2}\:[0-9]{2}\:[0-9]{2}", datelongest)[0]
        datelong = datetime.datetime.strptime(datelonger, "%Y-%m-%dT%H:%M:%S")
        date = str(datelong.month) + "/" + str(datelong.day) + "/" + str(datelong.year)
        starttime = str(datelong.time())
        if datelong.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        try:
            artist = bsObj.find("span", {"class":"artist-name"}).get_text().strip() # Event name
        except:
            artist = bsObj.find("h1", {"class":"headliners"}).get_text().strip()
        if "Private Event" in artist or "private-event" in newPage or "tap room open" in artist.lower() or "jokes on tap" in artist.lower() or artist == "The Southwester":
            continue
        if scraperLibrary.compactWord(artist) in localList:
            local = "Yes"
        else:
            local = ""
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]
        except:
            artistweb = newhtml
        artist = artist.replace('Free Acoustic','Acoustic')
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range...
        except:
            print("Is ", newhtml, "free?")
            price = "Free!"
        price = re.sub('(?i)general\sadmission\s*\-*\s*','',price)
        price = re.sub('(?i)ga\s*\-*\s*','',price)
        try:
            description = bsObj.find("div", {"class":"bio"}).get_text().strip()
        except:
            try:
                description = bsObj.find("h2", {"class":"additional-event-info"}).get_text().strip()
            except:
                description = ""

        if "will be held at Songbyrd" in description:
            continue
        description = re.sub('(PLEASE\sNOTE|Please\sNote)\:\s*The\scharge\son\syour\scredit\scard\swill\sshow\sup\sas\s\"(JAMMIN\sJAVA|Jammin\sJava)\"\.\s*(PLEASE\sNOTE|Please\sNote)\:\s*This\sshow\sis\sheld\sat\sThe\sMiracle\sTheatre\,\s535\s8th\sSt\sSE\,\s(Washington,\sDC)*\,*(\s20003)*','',description)
        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)

        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)

        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"]
        except:
            print("Could not find ticket link for", newhtml)
            ticketweb = ""
        musicurl = ""
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
            artistpic = bsObj.find("div", {"class":"event-detail"}).find("img").attrs["src"]
        except:
            artistpic = ""
        miracletest = bsObj.findAll("title")[0].get_text()
        if "Miracle Theatre" in miracletest:
            venuelink = "http://themiracletheatre.com/"
            venuename = "Miracle Theatre"
            addressurl = "https://goo.gl/maps/62b4LRVB4uP2"
            venueaddress = "535 8th St. SE, Washington, DC 20003"
        else:
            venuelink = "https://www.unionstage.com/"
            venuename = "Union Stage"
            addressurl = "https://goo.gl/maps/p5Jm72L1VVA2"
            venueaddress = "740 Water St SW, Washington, DC 20024"
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

fileName = '../scraped/usedlinks-union.csv'
backupFileName = '../scraped/BackupFiles/unionusedlinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

 
if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")