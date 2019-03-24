#Scrapes Flash events, using - http://www.flashdc.com/    


from urllib.request import urlopen #for pulling info from websites (will not be used if Error 403 encountered)
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime
import requests #for use if urllib doesn't work

import scraperLibrary #custom library for venue site scraping

pages = set() #create an empty set of pages
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to open used links file? (Skip previously-scraped links) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-flash.csv', 'r') as previousscrape:  
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime((line[1].strip()), '%B %d, %Y') #Date in table is in day month day, year format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

counter = 0 # A counter to track progress
UTFcounter = 0 # Counter for number of encoding problems

local = ""  # Add test for local in future
doors = "Doors:"
genre = "Rock & Pop"
venuelink = "https://www.flashdc.com/"
venuename = "Flash"
addressurl = "https://goo.gl/maps/fDfSwPV54Jr"
venueaddress = "645 Florida Ave. NW, Washington, DC 20001"
artistpic = "" 

csvFile = open('../scraped/scraped-flash.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/backupfiles/FlashScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

try:
    html = urlopen("http://www.flashdc.com/")
    bsObj = BeautifulSoup(html)
except:
    url = "http://www.flashdc.com/"
    bsObj = BeautifulSoup(requests.get(url).text)

for link in bsObj.findAll("a",href=re.compile("^(pages\/details)")): #The link to each unique event page begins with "pages/details"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        counter += 1
        newhtml = "http://www.flashdc.com/" + newPage
#        print(newhtml)
        try:
            html = urlopen(newhtml)
            bsObj = BeautifulSoup(html)
        except:
            bsObj = BeautifulSoup(requests.get(newhtml).text)
        datelong = bsObj.find("title").get_text() # This includes the name of the artist and "at Flash"
        date = re.findall("[A-Z][a-z]+\s+[0-9]{1,2}\,\s+[0-9]{4}", datelong)[0] # This pulls out the date
        dadate = datetime.datetime.strptime((date.strip()), '%B %d, %Y') #Date in table is in day month day, year format.
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
            continue
        artist = re.findall("(.+)\sat\sFlash", datelong)[0].strip()
        if "[OFF]" in artist or "[Off]" in artist or "(Off)" in artist or "(OFF)" in artist:
            continue
        artist = artist.replace("[in the Green Room]","")
        artist = re.sub('[\{\[\(][oO]pen[\s\-](2|to)[\s\-][cC]lose[\s\-]*[sS]*e*t*[\}\]\)]','',artist) {Open-2-Close}
        artist = re.sub('\[[lL][iI][vV][eE]\]','',artist)
        artistweb = ""
        musicurl = ""
        gotartistlink = False
        gotmusicurl = False
        try:
            datables = bsObj.findAll("table")
            for atable in datables:
                try:
                    herearelinks = atable.findAll("a")
                    for onelink in herearelinks:
                        try:
                            itsalink = onelink.attrs["href"]
                            simplyatest = urlopen(itsalink)
                            if gotartistlink == False:
                                artistweb = itsalink #First found link that works will be artist's link (hopefully)
                                gotartistlink = True
                            if gotmusicurl == False and (("soundcloud" in itsalink) or ("bandcamp" in itsalink)):  #Take first soundcloud or bandcamp url
                                musicurl = itsalink
                                gotmusicurl = True
                            elif gotmusicurl == False and "youtube" in itsalink:  #If no soundcloud or bandcamp, then take youtube
                                musicurl = itsalink
                                gotmusicurl = True
                        except:
                            continue
                        if gotartistlink == True and gotmusicurl == True:
                            break
                except:
                    continue
                if gotartistlink == True and gotmusicurl == True:
                    break
        except:
            artistweb = ""
        description = ""
        for onepara in bsObj.findAll("p"):
            try:
                howaboutthis = onepara.get_text().strip()
                if howaboutthis.startswith("website") or howaboutthis.startswith("soundcloud") or howaboutthis.startswith("music |") or howaboutthis.startswith("resident advisor") or "645 Florida" in howaboutthis or "Copyright" in howaboutthis:
                    continue
                else:
                    description += howaboutthis + " "
            except:
                continue

        [description, readmore] = scraperLibrary.descriptionTrim(description, ["facebook","resident advisor","twitter","soundcloud"], 700, artistweb, newhtml)

        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)

        description = re.sub('music\s+\|','',description)
        description = description.replace("|"," ")
        try:
            ticketweb =  bsObj.find("a", {"id":"hypTickets"}).attrs["href"]
        except:
            ticketweb = ""
        findthetime = bsObj.findAll("div", {"class":"col-12"})
        starttime = ""
        for onediv in findthetime:
            try:
                starttime = re.findall("Doors\:*\s+([0-9]{1,2}\:[0-9]{2}\s+[aApP][mM])", onediv.get_text())[0]
            except:
                anotherdiv = "bitesthedust"
        price = "Check ticket link for pricing"  # Flash doesn't list the ticket price on their website. They use a variety of ticket sales sites, but Ticketfly is their primary site, and its security blocks scraping.
        if ticketweb == "#":
            ticketweb = newhtml
        print("about to print, date = ", date, "artist = ", artist)
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
    linksBackup = "../scraped/backupfiles/FlashUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-flash.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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