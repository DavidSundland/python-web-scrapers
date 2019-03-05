#Scrapes Songbyrd events, using - http://www.songbyrddc.com/events/  

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

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

counter = 0  #to keep track of progress while program running
UTFcounter = 0

local = ""  # Add test for local in future
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "http://www.songbyrddc.com/"
venuename = "Songbyrd Cafe"
addressurl = "https://goo.gl/maps/Vnzq6cjvcjv"
venueaddress = "2477 18th St. NW, Washington, DC 20009"
musicurl = ""  ########## Make another attempt to extract musicurls in the future

csvFile = open('../scraped/scraped-songbyrd.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/SongbyrdScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.songbyrddc.com/events/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/shows\/)")): #The link to each unique event page begins with "/shows/"
    newPage = link.attrs["href"] #extract the links
    try:
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
            chitchat = "Hey, how about that local team?"
    if newPage not in pages: #A new link has been found
#        counter += 1
        newhtml = "http://www.songbyrddc.com" + newPage
        artistweb = newhtml
        eventhtml = urlopen(newhtml)
        eventObj = BeautifulSoup(eventhtml)
        print(newhtml)
        price = eventObj.find("div",{"class":"event-cost"}).get_text().strip()
        if "sold out" in price.lower():
            continue
        price = price.replace("Facebook RSVP","")
        price = price.replace("BUY TICKETS","")
        price = price.replace("FREE RSVP","")
        price = price.replace("RSVP!","")
        price = price.replace("RSVP","")
        price = price.strip()
        artistlong = eventObj.find("title").get_text().strip()
        artist = re.findall("(.+)\s+\@",artistlong)[0].title()
        if "listening party" in artist.lower() or "music trivia" in artist.lower() or "watch party" in artist.lower() or "diary of an r&b classic" in artist.lower():
            continue
        date = eventObj.find("span", {"class":"eventDate"}).attrs["v"]
        ticketweb = eventObj.find("a",{"class":"eventbtn"}).attrs["href"]
        dadate = datetime.datetime.strptime(date, '%d-%b-%Y')  #date is in "01-Jul-2018" format
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
            
        ##### MARK - CONTINUE FROM HERE; MAKE SURE TO UN-INDENT APPROPRIATELY; NOTE THAT TIME CAN BE IN "12:00 PM" OR "12 PM" FORMAT.  ALWAYS PRECEDED BY "DOORS" &/OR "SHOW"?
        xss = eventObj.findAll("div",{"class":"col-xs-6"})
        for onexs in xss:
            if re.search("[sS][hH][oO][wW]\:*\s?[0-9]{1,2}",onexs.get_text()):
                try:
                    starttime = re.findall("[sS][hH][oO][wW]\:*\s+([0-9]{1,2}\:?[0-9]{0,2}\s+[aApP][mM])",onexs.get_text())[0]
                except:
                    starttime = re.findall("[sS][hH][oO][wW]\:*\s+([0-9]{1,2}\:?[0-9]{0,2})",onexs.get_text())[0] + "PM"
                    print("in starttime except; is AM/PM correct?")
#                print(starttime, date)
                break
        doors = " "
        artistpic = ""
        pics = eventObj.findAll("img")
        for apic in pics:
            if not apic.attrs["src"].startswith("/images"):
                artistpic = "https://www.songbyrddc.com" + apic.attrs["src"]
        descriptionfinder = eventObj.find("div", {"class":"event-description"})
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
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        description = description.replace("ON SALE NOW!","")
        description = description.strip()
        description = description.strip("--")  # If description now leads w/ this, bye-bye
        if (len(description) > 700): # If the description is too long...  
            descriptionsentences = description.split(". ") #Let's split it into sentences!
            description = ""
            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                description += sentence + ". "
                if (len(description) > 650):  #Once we exceed 650, dat's da last sentence
                    break
#            readmore = newhtml #No longer using the readmore for extra long descriptions, since link to event provided...
#        else:
#            readmore = "" #We included the full description, so no need to have a readmore link
        readmore = "" ###################### KEEP CHECKING IN FUTURE TO SEE IF THEY START CONSISTENTLY PROVIDING LINK TO ARTIST WEBSITE
        try:  # Might crash with weird characters.
            writer.writerow((date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
            backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
        except:
            UTFcounter += 1
            try:
                writer.writerow((date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                print("Using UTF encoding for description", date)
            except:
                writer.writerow((date, genre, artistpic, local, doors, price, starttime, artistweb, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, artistweb, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
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
    linksBackup = "../scraped/BackupFiles/SongbyrdUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-songbyrd.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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