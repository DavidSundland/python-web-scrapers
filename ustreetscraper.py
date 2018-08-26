#Scrapes U Street Music Hall events, using - http://www.ustreetmusichall.com/calendar/  

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
    with open('../scraped/usedlinks-ustreet.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        try:
            dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Newer dates in table are 2017-12-16 format.
        except:
            try:
                dadate = datetime.datetime.strptime((line[1].strip()) + ' 2017', '%B %d %Y') #Date in table is in month day format (may be 1 or two spaces in-between).  ADDED YEAR - UPDATE BEFORE 2018
            except:
                try:
                    dadate = datetime.datetime.strptime((line[1].strip()) + ' 2017', '%A %B %d %Y')   ##############   ADDED YEAR - UPDATE BEFORE 2018
                except:
                    dadate = datetime.datetime.strptime((line[1].strip()) + ' 2017', '%A %b %d %Y')   ##############   ADDED YEAR - UPDATE BEFORE 2018
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

counter = 0 # A counter to track progress
UTFcounter = 0 # Counter for number of encoding problems

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop" 
artistpic = ""
ulink = "http://www.ustreetmusichall.com/"
uname = "U Street Music Hall"
umap = "https://goo.gl/maps/S5PQVPXGySK2"
uaddress = "1115 U St NW, Washington, DC 20009"
tigerslink = "http://www.tentigersdc.com/"
tigersname = "Ten Tigers"
tigersmap = "https://goo.gl/maps/QmFCBGtQVxn"
tigersaddress = "3813 Georgia Ave NW, Washington, DC 20011"

csvFile = open('../scraped/scraped-ustreet.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/UStreetScraped" + datetoday + ".csv"
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCVS)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.ustreetmusichall.com/calendar/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        counter += 1
        newhtml = "http://www.ustreetmusichall.com" + newPage
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        dadate = bsObj.find("h2", {"class":"dates"}).get_text().strip() # This includes the day of the week
#        date = re.findall(",\s+([a-zA-Z]+\s+[0-9]+)", datelong)[0] # WEBSITE CHANGED - This USED TO pull out the date
        year = today.year
        try:
            date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%B %d %Y').date()
        except:
            try:
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%A %B %d %Y').date()
            except:
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%A %b %d %Y').date()
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
            try:
                date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%B %d %Y').date()
            except:
                try:
                    date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%A %B %d %Y').date()
                except:
                    date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%A %b %d %Y').date()
        if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        starttime = bsObj.find("span", {"class":"start"}).get_text() # Pulls time, including pm
        starttime = starttime.replace("Show:", "").strip() # U Street has been adding 'Show:' text to time field of late...
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range
        except:   #Crashed with free event; woulda crashed w/ TBA event...
            try:
                price = bsObj.find("h3", {"class":"free"}).get_text().strip()  # Free event(s) actually have the price listed in an h3 w/ a class of 'free'
            except:
                print("Skipped",newPage,date,"because could not find price")
                continue
        artist = bsObj.find("h1", {"class":"headliners summary"}).get_text() # Event / top artist name
        artist = artist.replace("[open to close]","")
        artist = artist.replace("(open to close)","")
        if "at 9:30 Club" in artist or "Union Stage" in artist or "Cancelled" in artist or "CANCELLED" in artist:  # Annoyingly, 9:30 or Union Stage events may be included in U Street calendar - skip those
            continue
        if "Ten Tigers" in artist:
            venuelink = tigerslink
            venuename = tigersname
            addressurl = tigersmap
            venueaddress = tigersaddress
            artist = artist.replace("(at Ten Tigers)","") # perform the replacement w/in this "if" to avoid removing 10 Tigers from artist if misses this test
            artist = artist.replace("(At Ten Tigers)","")
        else:
            venuelink = ulink
            venuename = uname
            addressurl = umap
            venueaddress = uaddress
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - not all artists have a link, so...
        except:
            artistweb = newhtml
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"bio"}).get_text() # Get the description, which does include a lot of breaks - will it be a mess?
        except:
            description = ""
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        description = description.strip()
        if (len(description) > 600): # If the description is too long...  NOTE - U Street gets shorter descriptions
            descriptionsentences = description.split(". ") #Let's split it into sentences!
            description = ""
            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                description += sentence + ". "
                if (len(description) > 550):  #Once we exceed 600, dat's da last sentence
                    break
            readmore = artistweb #We had to cut it short, so you can read more at the event page UNLESS we found an artist link (in which case, go to their page)
        elif artistweb != newhtml:  #If description is short and we found an artist link (so artistweb is different than event page)
            readmore = artistweb #Have the readmore link provide more info about the artist
        else:
            readmore = "" #No artist link and short description - no need for readmore
        musicurl = ""
        try:
            musicurl = bsObj.find("li", {"class":"soundcloud"}).find("a").attrs["href"]
        except:
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
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door
        except:
            ticketweb = ""
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
        print(counter)
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/UStreetUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-ustreet.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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
