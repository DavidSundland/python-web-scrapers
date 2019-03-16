#Scrapes Anthem's events, using - http://www.theanthemdc.com/calendar/  

from urllib.request import urlopen #for pulling info from websites

import requests  # due to changes in site's encoding, needed to add this import

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
    with open('../scraped/usedlinks-anthem.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime((line[1].strip()), '%m/%d/%Y') #Date in table is in  10/31/2017 format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
            try:  # Check to make sure that previously scraped events are still valid
                forgotPartOfLink = "http://www.theanthemdc.com" + line[0]
                diditwork = urlopen(forgotPartOfLink)
            except:
                print(forgotPartOfLink,"caused an error...")
    previousscrape.close()

UTFcounter = 0

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "https://www.theanthemdc.com/"
venuename = "Anthem"
addressurl = "https://goo.gl/maps/QHoa2MXg5762"
venueaddress = "901 Wharf Street SW, Washington, DC 20024"

csvFile = open('../scraped/scraped-anthem.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/backupfiles/anthemscraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

# html = urlopen("https://www.theanthemdc.com/calendar/")  # due to changes in site's encoding, this no longer works
# bsObj = BeautifulSoup(html)

html = "https://www.theanthemdc.com/calendar/"
bsObj = BeautifulSoup(requests.get(html).text)

# print(bsObj)

for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "https://www.theanthemdc.com" + newPage
        print("newhtml:",newhtml, ", about to open link")
#        bshtml = urlopen(newhtml) # due to changes in site's encoding, this no longer works
#        print("opened link")
#        bsObj = BeautifulSoup(bshtml)
#        print("successfully created BS object")
        bsObj = BeautifulSoup(requests.get(newhtml).text)
        try:
            bsObj.find("h3", {"class":"cancelled"}).get_text()  #if this DOESN'T fail, event is cancelled - skip it
            continue
        except:
            notcancelled = True
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range...
        except:
            print("COULD NOT FIND PRICE for", newhtml)
            continue
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
            artist = bsObj.find("h1", {"class":"headliners"}).get_text().strip() # If no artist description, then no 'artist-name' span
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a div with a class of "music_links", then digs deeper, finding the first instance w/in that div of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = newhtml
        try:
            description = bsObj.find("div", {"class":"bio"}).get_text().strip()
        except:
            try:
               description = bsObj.find("div", {"id":"additional-ticket-text"}).get_text().strip()
            except:
                print("COULD NOT FIND BIO for ", newhtml)
                description = ""
        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)

        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            scraperLibrary.killCapAbuse(description)
        
        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"]
        except:
            print("COULD NOT FIND TICKET LINK for", newhtml)
            pages.add(newPage)
            pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
            continue
        musicurl = ""
        try:   
            artistpic = bsObj.find("div", {"class":"event-detail"}).find("img").attrs["src"]
        except:
            artistpic = ""
        try:  # Might crash with weird characters.
            writer.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
            backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
        except:
            UTFcounter += 1
            try:
                writer.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                print("Using UTF encoding for description", date)
            except:
                writer.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
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
    linksBackup = "../scraped/BackupFiles/anthemusedlinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-anthem.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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