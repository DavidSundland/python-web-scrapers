#Scrapes Black Cat's events, using - http://www.blackcatdc.com/schedule.html  

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
    answer = input("Do you open used links file? (Avoid scraping previously scraped links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-blackcat.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Dates in table are 2018-07-16 format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

counter = 0
UTFcounter = 0 # Counter for number of encoding problems

local = ""  # Add test for local in future
doors = "Doors:"
genre = "Rock & Pop"
venuelink = "http://www.blackcatdc.com/"
venuename = "Black Cat"
addressurl = "https://goo.gl/maps/MbEJL3TaYbA2"
venueaddress = "1811 14th St. NW, Washington, DC 20009"

csvFile = open('../scraped/scraped-blackcat.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(today)
backupfile = "../scraped/BackupFiles/blackcatscraped" + datetoday + ".csv"
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCVS)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.blackcatdc.com/schedule.html")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(http\:\/\/www\.blackcatdc\.com\/shows\/)")): #The link to each unique event page begins with "http://www.blackcatdc.com/shows/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        counter += 1
        newhtml = newPage
        print("######   Extracting info from:   ",newhtml)
        try:  # Just in case they provide a broken link
            html = urlopen(newhtml)
            bsObj = BeautifulSoup(html)
        except:
            print("!!!!!!! !!!!!  !!! !!!!!!    !!!!!! Skipped ", newhtml, "!!! !!!!! !!!!!!!!!!!")
            continue
        issoldout = False
        try:
            soldoutcheck = bsObj.findAll("h2", {"class":"support"})
            for onecheck in soldoutcheck:
                if "SOLD OUT" in onecheck.get_text() or "Sold Out" in onecheck.get_text() or "sold out" in onecheck.get_text():
                    issoldout = True
                    break
        except:
            gotnosupport = True
        if issoldout == True:
            continue
        try:
            artistallcap = bsObj.find("h1", {"class":"headline"}).get_text()
        except:
            print("Found no 'headline' for", newhtml, " - external link?")
            continue
        if "RED ROOM" in artistallcap or "CHURCH NIGHT" in artistallcap or "TEN FORWARD" in artistallcap or "DR. WHO" in artistallcap or "HEAVY ROTATION" in artistallcap or "MUGGLE MONDAYS" in artistallcap:
            continue
        byebyecaps = artistallcap.split()
        artist = ""
        for word in byebyecaps:
            artist += word.capitalize() + " "
        artist = artist.replace("Dc","DC")
        if "story district" in artist.lower():
            continue
        year = today.year
        dadate = bsObj.find("h2", {"class":"date"}).get_text() # This includes the day of the week.  The spreadsheet doesn't care.
        try:
            date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%A %B %d %Y').date() #Date is in day of week month day format. Month format varies.
            if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%A %B %d %Y').date()
        except:
            try:
                dadate = dadate.replace("Sept","Sep")
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%A %b %d %Y').date() #Date is in day of week month day format. 
                if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
                    date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%A %b %d %Y').date()
            except:
                print("Date for ", newhtml, " was funky - is it a date range?")
                continue
        if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
            continue
        showtextps = bsObj.findAll("p", {"class":"show-text"})
        price = "Free"
        starttime = "aintnone"
        for oneresult in showtextps:
#            print(oneresult.get_text())
            try:
                longtime = re.findall("Doors\sat\s([0-9]{1,2}:[0-9]{2})", oneresult.get_text())[0] #This extracts the time
                timesplit = longtime.split(":")
                starttime = str(int(timesplit[0]) + 12) + ":" + timesplit[1]  # Add 12 to the time to make it p.m. (all Black Cat events are pm (I hope))
            except:
                hey = "how about that weather"
            try:  # Some of the show-text paragraphs have no content...
                if "Adv" in oneresult.get_text() and "DOS" in oneresult.get_text():
                    price = re.findall("\$[0-9]{1,3}", oneresult.get_text())[0] + " in advance, " + re.findall("\$[0-9]{1,3}", oneresult.get_text())[1] + " D.O.S."
                else:
                    price = re.findall("\$[0-9]{1,3}", oneresult.get_text())[0]
            except:
                freedom = "not free"
        if price == "Free":
            print("Make sure that",date,artist,"is indeed free")
        if starttime == "aintnone":
            print("Skipping", newhtml, ", time not found.")
            continue
        try:
            artistweb = bsObj.find("h1", {"class":"headline"}).find("a").attrs["href"]  #THIS finds the first instance of an h1 with a class of "headline", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = ""
        try: # There isn't always a description...
            description = bsObj.find("p", {"id":"bio"}).get_text()
        except:
            description = ""
            
        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)

        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)
        try:
            iframes = bsObj.findAll("iframe").attrs["src"] # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
            for onei in iframes:
                if "youtube" in onei:
                    musicurl = onei
                    continue  # Once first video is found, move along (don't take back-up band's video over headliner; don't have 'else' overwrite found link)
                else:
                    musicurl = ""  # In case there are iframes, but no videos
        except:
            musicurl = ""
        try:
            ticketweb = bsObj.find("a", href=re.compile("^(https\:\/\/www\.ticketfly\.com)")).attrs["href"]  #Ticket link - hopefully first Ticketfly link is for THIS event
        except:
            ticketweb = ""
        try:   
            artistpic = "http://www.blackcatdc.com" + bsObj.find("div", {"class":"band-photo-big"}).find("img").attrs["src"]
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
        pages.add(newPage)  # Adding link to list at end, in case item skipped 'cuz not yet info on site (get it later)
        pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
#        print(counter)
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/blackcatusedlinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-blackcat.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")
