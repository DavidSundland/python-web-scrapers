#Scrapes Songbyrd events, using - http://www.songbyrddc.com/events/  

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


pages = set() #create an empty set of pages
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""
while answer not in yesno:  
    answer = input("Do you want to open used links file? (Skip previously-used links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-songbyrd.csv', 'r') as previousscrape:  
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        # NOTE!  For other sites, links to old events are removed from scraped CSV file.  But Songbyrd NEVER removes event links from the events page, it merely hides past events.  So the Songbyrd scraped CSV lists ALL links that have EVER been checked.
        pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
        pages.add(line[0])
    previousscrape.close()

UTFcounter = 0

local = "" 
genre = "Rock & Pop"
venuelink = "http://www.songbyrddc.com/"
venuename = "Songbyrd Cafe"
addressurl = "https://goo.gl/maps/Vnzq6cjvcjv"
venueaddress = "2477 18th St. NW, Washington, DC 20009"

fileName = '../scraped/scraped-songbyrd.csv'
backupFileName = '../scraped/BackupFiles/SongbyrdScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)

html = urlopen("http://www.songbyrddc.com/events/")
eventObj = BeautifulSoup(html)
for link in eventObj.findAll("a",href=re.compile("^(\/shows\/)")): #The link to each unique event page begins with "/shows/"
    newPage = link.attrs["href"] #extract the links
    try: # event URLs include the date, in one of two formats
        dateonly = re.findall("[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}",newPage)[0]
        dadate = datetime.datetime.strptime(dateonly, '%Y-%m-%d') # If this is a past event...
        if (dadate.date() < today):
            pages.add(newPage)
            pageanddate.add((newPage,str(dadate),datetoday)) # Add to file so not scraped in future
            continue
    except:
        try:
            dateonly = re.findall("[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{4}",newPage)[0]
            dadate = datetime.datetime.strptime(dateonly, '%m-%d-%Y') # If this is a past event...
            if (dadate.date() < today):
                pages.add(newPage)
                pageanddate.add((newPage,str(dadate),datetoday)) # Add to file so not scraped in future
                continue
        except:
            continue # if date not in URL, not for a live music event
    if newPage not in pages: #A new link has been found
        newhtml = "http://www.songbyrddc.com" + newPage
        artistweb = ""
        eventhtml = urlopen(newhtml)
        bsObj = BeautifulSoup(eventhtml)
        print(newhtml)
        price = bsObj.find("div",{"class":"event-cost"}).get_text().strip()
        if "sold out" in price.lower():
            continue
        price = price.replace("BUY TICKETS","")
        price = re.sub('(Facebook\s)*(Free\s)*(FREE\s)*RSVP\!*','',price)
        price = price.strip()
        artistlong = bsObj.find("title").get_text().strip()
        artist = re.findall("(.+)\s+\@",artistlong)[0].title()
        skipArtists = ["punkhouse comedy","listening party","music trivia","karaoke.sexy","watch party","diary of an r&b","classic album sundays","@ dangerous","@ milkboy","@ union","@ fillmore","cancelled"]
        skip = False
        for skipArtist in skipArtists:
            if skipArtist in artist.lower():
                skip = True
                break
        if skip:
            continue
        artist = artist.replace("Project Hera Presents: ","")
        date = bsObj.find("span", {"class":"eventDate"}).attrs["v"]
        ticketweb = bsObj.find("a",{"class":"eventbtn"}).attrs["href"]
        dadate = datetime.datetime.strptime(date, '%d-%b-%Y')  #date is in "01-Jul-2018" format
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
            
        xss = bsObj.findAll("div",{"class":"col-xs-6"})
        for onexs in xss:
            if re.search("[sS][hH][oO][wW]\:*\s?[0-9]{1,2}",onexs.get_text()):
                try:
                    starttime = re.findall("[sS][hH][oO][wW]\:*\s+([0-9]{1,2}\:?[0-9]{0,2}\s+[aApP][mM])",onexs.get_text())[0]
                except:
                    starttime = re.findall("[sS][hH][oO][wW]\:*\s+([0-9]{1,2}\:?[0-9]{0,2})",onexs.get_text())[0] + "PM"
                    print("in starttime except; is AM/PM correct?")
                break
        doors = " "
        artistpic = ""
        pics = bsObj.findAll("img")
        for apic in pics:
            if not apic.attrs["src"].startswith("/images"):
                artistpic = "https://www.songbyrddc.com" + apic.attrs["src"]
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
        descriptionfinder = bsObj.find("div", {"class":"event-description"})
        description = ""
#        divcounter = 1
        parts = descriptionfinder.findAll(["div","p"])
        for onepart in parts:
                thetext = onepart.get_text().strip()
                # next lines skip extraneous crap
                if len(thetext) < 5:  #skip crap such as "--"
                    continue
                if "presents" in thetext.lower():
                    continue
                if thetext.lower().startswith("free") and len(thetext) < 50:
                    continue
                if thetext.lower().startswith("on sale") and len(thetext) < 30:
                    continue
                if re.search("^[SMTWF][UOEHRAuoehra][A-Za-z]+\,*\s+[JFMASOND][AEPUCOaepuco][a-zA-Z]+\s+[0-9]{1,2}",thetext):  #Skip day and date
                    continue
                if re.search("^[JFMASOND][AEPUCOaepuco][a-zA-Z]+\s+[0-9]{1,2}",thetext) and len(thetext) < 30: #Skip date if not start of longer description
                    continue
                if re.search("^\$[0-9]{1,3}",thetext) and len(thetext) < 50: #Skip prices
                    continue
                if artist.lower() == thetext.lower():  #don't need to re-list artist name in description
                    continue
                if thetext.lower().startswith("vinyl lounge"):
                    continue
                description += thetext + " "
        description = description.strip()
        description = description.strip("--")  # If description now leads w/ this, bye-bye

        [description, readmore] = scraperLibrary.descriptionTrim(description, ["ON SALE NOW!","LiveNation and Songbyrd Present ","Songbyrd Presents ","Songbyrd Vinyl Lounge "], 800, artistweb, newhtml)

        write1 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb)
        write2 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
        write3 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
        try:  # Might crash with weird characters.
            writer.writerow((write1))
            backupwriter.writerow((write1))
        except:
            UTFcounter += 1
            try:
                writer.writerow((write2))
                backupwriter.writerow((write2))
                print("Using UTF encoding for description", date)
            except:
                writer.writerow((write3))
                backupwriter.writerow((write3))
                print("Using UTF encoding for artist and description", date)
        pages.add(newPage)
        pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
csvFile.close()
backupCSV.close()

fileName = '../scraped/usedlinks-songbyrd.csv'
backupFileName = '../scraped/BackupFiles/SongbyrdUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")