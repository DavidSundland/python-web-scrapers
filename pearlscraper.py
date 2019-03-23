#Scrapes Pearl's events, using - http://www.pearlstreetwarehouse.com/shows/  
#DO, FUTURE - figure out system for genre and local...

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-pearl.csv'
dateFormat = '%m/%d/%Y'
numDays = 30
linkCheckUrl = "http://www.pearlstreetwarehouse.com"

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)

UTFcounter = 0

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "http://www.pearlstreetwarehouse.com/"
venuename = "Pearl Street Warehouse"
addressurl = "https://goo.gl/maps/4QquQtVkmcE2"
venueaddress = "33 Pearl St SW, Washington, DC 20024"

csvFile = open('../scraped/scraped-pearl.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/PearlScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.pearlstreetwarehouse.com/shows/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "http://www.pearlstreetwarehouse.com" + newPage
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range...
        except:
            price = "Free!"  # In the first instance in which price-range failed, event was free...
            if "free" not in newhtml:
                print("Verify that ", newhtml, " is indeed free!!!!!!!")
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
            artist = bsObj.find("h1", {"class":"headliners"}).get_text().strip() # Event name
        if "private event" in artist.lower():
            continue
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a div with a class of "music_links", then digs deeper, finding the first instance w/in that div of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = ""
        try:
            description = bsObj.find("div", {"class":"bio"}).get_text().strip()
        except:
            description = ""
            try:
                parts = bsObj.find("h1", {"class":"headliners"}).get_text().strip()
                for onepart in parts:
                    description += onepart + " "
            except:
                print("couldn't find description...")

        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)
        
        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)

        try:
            ticketurl = bsObj.find("a", {"class":"tickets"}).attrs["href"]
        except:
            print("Could not find ticket link for", newhtml)
            ticketurl = ""
        musicurl = ""
        try:
            iframes = bsObj.findAll("iframe") # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
            for onei in iframes:  
                if "youtube" in onei.attrs["src"]:
                    musicurl = onei.attrs["src"]
                    break  # Once first video is found, move along (don't take back-up band's video over headliner; don't have 'else' overwrite found link)
                else:
                    musicurl = ""  # In case there are iframes, but no videos
        except:
            musicurl = ""
        try:   
            artistpic = bsObj.find("div", {"class":"event-detail"}).find("img").attrs["src"]
        except:
            artistpic = ""
        write1 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketurl)
        write2 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl)
        write3 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl)
        
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

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/PearlUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-pearl.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
    backupLinks = open(linksBackup, 'w', newline='')
    linkswriter = csv.writer(linksFile)  #Write the file at the end so file is not overwritten if error encountered during scraping
    backupWriter = csv.writer(backupLinks)
    for heresalink in pageanddate:
        linkswriter.writerow((heresalink[0], heresalink[1], heresalink[2])) # Write this event to a file so that it will be skipped during future scrapes 
        backupWriter.writerow((heresalink[0], heresalink[1], heresalink[2]))
    linksFile.close()
    backupLinks.close()
    print("New used links file created.")
else:
    print("New used links file was NOT created.")
    
if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")