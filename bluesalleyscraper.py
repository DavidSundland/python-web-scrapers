
from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import datetime
import csv #comma-separated values

import scraperLibrary #custom library for venue site scraping

pages = set() #create an empty set of pages
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you open used links file? (Avoid scraping previously scraped links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-bluesalley.csv', 'r') as previousscrape:
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d')
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

# UTFcounter = 0 # Counter for number of encoding problems (thusfar not needed for Blues Alley)

localList = scraperLibrary.getLocalList()


doors = " "
genre = "Jazz & Blues"
venuelink = "http://www.bluesalley.com/"
venuename = "Blues Alley"
addressurl = "https://goo.gl/maps/KKBK333pbxu"
venueaddress = "1073 Wisconsin Ave. NW, Washington, DC 20007"

csvFile = open('../scraped/scraped-bluesalley.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(today)
backupfile = "../scraped/BackupFiles/bluesalleyscraped" + datetoday + ".csv"
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCVS)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.bluesalley.com/events.cfm")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile(".+home\.event.+")): #The link to each unique event page includes "home.event"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        print(newPage)
        pages.add(newPage)
        newhtml = newPage # An extra line of code; used 'cuz in some cases a site's base URL needs to be added to the internal link
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        artistweb = newhtml
        musicurl = ""
        artist = bsObj.find("h1", {"class":"event-title"}).get_text() #This gets the event name (including extra description in some cases)
        if scraperLibrary.compactWord(artist) in localList:
            local = "Yes"
        else:
            local = ""
        if "closed" in artist.lower():
            continue
        try:  #When artist website is provided, it is in one of the "description" paragraphs (always the fourth?)
            alldaps = bsObj.findAll("p", {"class":"description"})
            for onep in alldaps:
                try:
                    artistweb = onep.findAll("a")[0].attrs["href"]
                    try:
                        isvalidlink = urlopen(artistweb) #test to make sure that link isn't broken
                    except:
                        artistweb = newhtml
                    try:
                        secondlink = onep.findAll("a")[1].attrs["href"]
                        if "youtube" in secondlink:
                            try:
                                isavid = urlopen(secondlink) #test to make sure link ain't broken
                                musicurl = secondlink
                            except:
                                musicurl = ""
                    except:
                        aintnovideo = True
                except:
                    hootnow = "bewowza"
        except:
            hootnow = "surewhynot"
        datelong = bsObj.find("span", {"class":"start-time"}).get_text()  # This pulls out all of the text - the day of the week, the date, the start time, and the price. Need to extract the date, time, and cost.
        if len(datelong) == 0:
            datelong = bsObj.find("span", {"id":"event-date"}).get_text()
        year = today.year
        date = re.findall(",\s([a-zA-Z]+\s[0-9]+)", datelong)[0] #This pulls out the date
        dateonly = datetime.datetime.strptime((date.strip() + ' ' + str(year)), '%B %d %Y').date() #Date is in "March 16" format; year added.
        if dateonly < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
            dateonly = datetime.datetime.strptime((date.strip() + ' ' + str(year + 1)), '%B %d %Y').date()
        if dateonly > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it (a lot can happen in 2 months):
            continue
        pageanddate.add((newPage,dateonly,datetoday))  # Add link to list, paired with event date and today's date
        starttime = str(int(re.findall("[\n\r]([0-9]+)", datelong)[0])+12)+":00" #This extracts the number portion of the time, converts it to an integer, adds 12 ('cuz all Blues Alley events in eve), converts to a string, and adds :00.
        if "free" in datelong.lower():
            price = "Free!"
        else:
            price = re.findall("\$[0-9]+", datelong)[0]  #This extracts the ticket price
        descriptionparagraphs = list(bsObj.find("p", {"class":"description"}).next_siblings) # Gets the description.
        description = "" #Create an empty string
        counter = 0  #Need to create a loop in order to be able to use the .get_text thingie
        while (counter < len(descriptionparagraphs)):
            try: #The content (or lack thereof) of some paragraphs cause fatal errors
                description += descriptionparagraphs[counter].get_text() + " \u00A4 "  # Description may be split between multiple paragraphs.  A symbol is concatenated in case, say, the site lists each musician in a separate paragraph.
                counter += 1
            except:
                counter += 1
        description = re.sub('\s+',' ',description)
        description = description.replace("\u00A4 \u00A4","\u00A4") # In case symbol occurs two times in a row
        
        [description, readmore] = scraperLibrary.descriptionTrim(description, ["Watch Video","Visit Website"], 800, artistweb, newhtml)

        images = bsObj.findAll("img")
        artistpic = ""
        for oneimage in images: 
            if "photos" in oneimage.attrs["src"] and starttime != "22:00" and starttime != "23:00":  #Pulls photo from site IF not the late show (only want pics for one show per day)
                artistpic = "http://www.bluesalleylive.com" + oneimage.attrs["src"]
                break
        ticketweb = newhtml
        writer.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
        backupwriter.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
#        print(loopcounter)
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/bluesalleyusedlinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-bluesalley.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
    backupLinks = open(linksBackup, 'w', newline='')
    linkswriter = csv.writer(linksFile)  #Write the file at the end so file is not overwritten if error encountered during scraping
    backupWriter = csv.writer(backupLinks)
    for heresalink in pageanddate:
        try:  # Encountered tuple index out of range error here before - don't know why a tuple had fewer than 3 items...
            linkswriter.writerow((heresalink[0], heresalink[1], heresalink[2])) # Write this event to a file so that it will be skipped during future scrapes 
            backupWriter.writerow((heresalink[0], heresalink[1], heresalink[2]))
        except:
            continue
    linksFile.close()
    backupLinks.close()
    print("New used links file created.")
else:
    print("New used links file was NOT created.")
