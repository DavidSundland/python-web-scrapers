#Scrapes Gypsy Sally's events, using - http://www.gypsysallys.com/calendar/  


#from urllib.request import urlopen #for pulling info from websites # this stopped working...
import requests #a substitute for urllib, which no longer works for ticketed Gypsy events
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
    with open('../scraped/usedlinks-gypsy.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime((line[1].strip()), '%a, %B %d, %Y') #Date in table is in d.o.w.(abbrev.), month day, year format.
        if dadate.date() > today-datetime.timedelta(days=122):  #If used link is NOT for an event that is more than 4 months old, add it to list
            # Gypsy's site keeps links for old events for a long time, so need to keep old links longer than for most sites
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
            testurl = "https://www.gypsysallys.com" + line[0]
            if dadate.date() > today-datetime.timedelta():
                try: #test to ensure that previously-scraped events are still valid...
                    diditwork = requests.get(testurl)
                    if diditwork.status_code > 299:
                        print("Trying to open", testurl, "event on", line[1], "returned an error code")
                except:
                    print("Trying to open", testurl, "event on", line[1], "did not work.")
    previousscrape.close()

counter = 0 # A counter to track progress
UTFcounter = 0 # Counter for number of encoding problems

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "http://www.gypsysallys.com/"
venuename = "Gypsy Sally's"
addressurl = "https://goo.gl/maps/omk3qVuLwWG2"
venueaddress = "3401 Water St. NW, Washington, DC 20007"

csvFile = open('../scraped/scraped-gypsy.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/GypsyScraped" + datetoday + ".csv"
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCVS)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

# html = urlopen("https://www.gypsysallys.com/listing/") # no longer works
# bsObj = BeautifulSoup(html)
url = "https://www.gypsysallys.com/listing/"
bsObj = BeautifulSoup(requests.get(url).text)

for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        # counter += 1
        newhtml = "http://www.gypsysallys.com" + newPage
        print(newhtml)
#        html = urlopen(newhtml) # no longer works...
#        bsObj = BeautifulSoup(html)
#        url = "https://www.gypsysallys.com/listing/"
        bsObj = BeautifulSoup(requests.get(newhtml).text)
        date = bsObj.find("h2", {"class":"dates"}).get_text() # This includes the day of the week, the year and, sometimes, extra spaces.  The spreadsheet doesn't care. (Including year good for E.O.Y.)
        try:
            dadate = datetime.datetime.strptime((date.strip()), '%a, %B %d, %Y') #Date in table is in day month day, year format.
        except:
            print("SKIPPED ", newhtml, date, "DATE RANGE, OR OTHER ISSUE?  IF DATE RANGE, PROBABLY MULTI-DAY PACKAGE, SO SHOULD BE SKIPPED ANYWAY?")
            continue
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
            continue
        time = bsObj.find("span", {"class":"dtstart"}).get_text() # Pulls time AND "Show:" (NOTE - also has class name of "start")
        starttime = re.findall("[0-9]{1,2}:[0-9]{2}\s*[aApP][mM]", time)[0] #This extracts the time, including am/pm
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range
        except:  # Let's hope that it's free if it doesn't have an h3 w/ a class of "price-range"
            price = "Free!"
        artist = bsObj.find("h1", {"class":"headliners summary"}).get_text() # Event / top artist name
        artist = artist.replace("VINYL LOUNGE OPEN MIC", "Vinyl Lounge Open Mic") # Eliminate annoying all-caps, if applicable
        artist = artist.replace(", VINYL LOUNGE", "") # Eliminate 'bonus' info about artist being @ Vinyl
        artist = artist.replace("Gordon Sterling Presents:", "")
        if "closed" in artist.lower() in artist: # Skip closed private events
            continue
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = newhtml
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"bio"}).get_text() # Get the description, which does include a lot of breaks - will it be a mess?
        except:
            description = ""

        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)

        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)
        
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
        ticketweb = ""
        try:
            ticketwad = bsObj.find("h3", {"class":"price-range"}).find_next_siblings()  #Ticket link not uniquely labeled - links to tickets to OTHER events have same labels as page's event...
            for brosis in ticketwad:
                try:
                    ticketweb = brosis.find("a", {"class":"tickets"}).attrs["href"]  #Event's ticket link (if applicable) is in one of the siblings to "price-range"
                except:
                    continue
        except:
            ticketweb = ""
        try:
            artistpic = bsObj.find("link", {"rel":"image_src"}).attrs["href"]
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
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/GypsyUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-gypsy.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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
