#Scrapes Howard Theatre's events, using - http://thehowardtheatre.com/calendar/  FOR SPREADSHEET, USE Scrapers - General


from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping

pages = set() #For list of used links 
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to open used links file? (Skip previously-used links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-howard.csv', 'r') as previousscrape:
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%A, %B %d, %Y') #Date in table is in day of week, month day, year format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is a month or more in the past, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before (skipping old ones, since unlikely to be encountered)
            pages.add(line[0])
    previousscrape.close()

UTFcounter = 0 # Counter for number of encoding problems
genre = "Rock & Pop"  #Add test for this in future
local = ""  #Add test for this in future
doors = " "
venuelink = "http://thehowardtheatre.com/"
venuename = "Howard Theatre"
addressurl = "https://goo.gl/maps/tDew7muhxrH2"
venueaddress = "620 T Street NW, Washington, DC 20001"
musicurl = ""   #Add test for this in future

datetoday = str(today)
backupfile = "../scraped/BackupFiles/HowardScraped" + datetoday + ".csv"
csvFile = open('../scraped/scraped-howard.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
writer = csv.writer(csvFile)
backupwriter = csv.writer(backupCVS)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://thehowardtheatre.com/calendar/")
bsObj = BeautifulSoup(html)
for javascript in bsObj.findAll("script", {"type":"text/javascript"}):
    totalcode = re.findall("(http\:\\\/\\\/thehowardtheatre\.com\\\/show\\\/[0-9]{4}\\\/[0-9]{2}\\\/[0-9]{2}\\\/[0-9a-zA-Z-]+\\\/)", javascript.get_text()) # Links are provided in format for Jquery, so need to remove the backslashes - an example of an original: "http:\/\/thehowardtheatre.com\/show\/2017\/02\/24\/cameo-2\/"
    for onefound in totalcode:
        if (onefound != ""): # Some list elements will be empty - skip those
            onepage = onefound.replace("\\", "") # Get rid of the backslashes
            if onepage not in pages: #A new link has been found
                try:
                    newhtml = urlopen(onepage)
                    eventObj = BeautifulSoup(newhtml)
                except:
                    print("Skipped:",onepage)
                    continue
                artist = eventObj.find("p", {"class":"show-primary-info-title"}).get_text() # Event / top artist name
                if artist == "Henny & Waffles":
                    continue
                eventdate = eventObj.find("p", {"class":"show-primary-info-showdate"}).get_text()
                dadate = datetime.datetime.strptime((eventdate.strip()), '%A, %B %d, %Y') #Date in table is in day month day, year format.
                if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
                    continue
                pageanddate.add((onepage,eventdate,datetoday))  # Add link to list, paired with event date and today's date
                pages.add(onepage) #Add link to list so redundant links are not checked
                time = eventObj.find("p", {"class":"show-primary-info-showtime"}).get_text() # Pulls time, including "Showtime @ "
                starttime = re.findall("([0-9]+:[0-9]{2}\s*[apAP][mM])", time)[0] #This extracts the time, including am/pm
                price = eventObj.find("p", {"class":"show-primary-info-tickets"}).get_text() # Pulls the price, which could be a price range, AND DOES INCLUDE "Tickets"
                if "$" not in price and "free" not in price.lower(): # No price indicated - skip it
                    continue
                price = price.replace("Tickets ","") #Get rid of leading text
                try:
                    artistweb = eventObj.find("p", {"class":"show-artist-website"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
                    try: #test the link to see if it works
                        doesitwork = urlopen(artistweb)
                    except:
                        artistweb = onepage
                        print("Encountered broken artist link for",eventdate)
                except:
                    artistweb = onepage
                description = ""
                try:  #bio is in a weird location...
                    biosiblings = eventObj.find("p", {"class":"show-artist-bio"}).find_next_siblings() # .find_next_siblings("p", limit=3)
                    for brosis in biosiblings:
                        description += brosis.get_text() + " "
                except:
                    print("Description find failed")
                
                [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)
                
                descriptionJammed = description.replace(" ","") # Create a string with no spaces
                if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
                    description = scraperLibrary.killCapAbuse(description)
                try:
                    ticketweb = eventObj.findAll("p", {"class":"show-primary-info-tickets"})[1].find("a").attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door and because ticket sales don't have unique identifier
                except:
                    print("Couldn't find ticket sales link for", eventdate)
                    ticketweb = onepage
                try:
                    artistpic = "http://thehowardtheatre.com" + eventObj.find("p", {"class":"show-artist-img"}).find("img").attrs["src"]
                except:
                    artistpic = ""
                try:  # Might crash with weird characters.
                    writer.writerow((eventdate, genre, artistpic, local, doors, price, starttime, onepage, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
                    backupwriter.writerow((eventdate, genre, artistpic, local, doors, price, starttime, onepage, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
                except:
                    UTFcounter += 1
                    try:
                        writer.writerow((eventdate, genre, artistpic, local, doors, price, starttime, onepage, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                        backupwriter.writerow((eventdate, genre, artistpic, local, doors, price, starttime, onepage, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                        print("Using UTF encoding for description", eventdate)
                    except:
                        writer.writerow((eventdate, genre, artistpic, local, doors, price, starttime, onepage, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                        backupwriter.writerow((eventdate, genre, artistpic, local, doors, price, starttime, onepage, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                        print("Using UTF encoding for artist and description", eventdate)
                print(onepage,eventdate)
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/HowardUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-howard.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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