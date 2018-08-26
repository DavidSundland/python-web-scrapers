#Scrapes Pearl's events, using - https://www.unionstage.com/listing/
#DO, FUTURE - figure out system for genre and local...

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
    with open('../scraped/usedlinks-union.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime((line[1].strip()), '%m/%d/%Y') #Date in table is in  10/31/2017 format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
            try:  # Check to make sure that previously scraped events are still valid
                tryitout = "https://www.unionstage.com" + line[0]
                diditwork = urlopen(tryitout)
            except:
                print(line[0],"caused an error...")
    previousscrape.close()

UTFcounter = 0

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future

csvFile = open('../scraped/scraped-union.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/UnionScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("https://www.unionstage.com/listing/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
#        counter += 1
        newhtml = "https://www.unionstage.com" + newPage
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range...
        except:
            print("Is ", newhtml, "free?")
            price = "Free!"
        datelongest = bsObj.find("span", {"class":"value-title"}).attrs["title"]  # To make sure getting date/time from this event and not future event, pull from attributes (also - includes year)
        datelonger = re.findall("20[12][0-9]\-[0-2][0-9]\-[0-3][0-9]T[0-9]{2}\:[0-9]{2}\:[0-9]{2}", datelongest)[0]
        datelong = datetime.datetime.strptime(datelonger, "%Y-%m-%dT%H:%M:%S")
        date = str(datelong.month) + "/" + str(datelong.day) + "/" + str(datelong.year)
        starttime = str(datelong.time())
        if datelong.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        try:
            artist = bsObj.find("span", {"class":"artist-name"}).get_text().strip() # Event name
        except:
            artist = bsObj.find("h1", {"class":"headliners"}).get_text().strip()
        if "Private Event" in artist or "private-event" in newPage:
            continue
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]
        except:
            artistweb = newhtml
        try:
            description = bsObj.find("div", {"class":"bio"}).get_text().strip()
        except:
            try:
                description = bsObj.find("h2", {"class":"additional-event-info"}).get_text().strip()
            except:
                description = ""
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        if (len(description) > 700): # If the description is too long...  
            descriptionsentences = description.split(". ") #Let's split it into sentences!
            description = ""
            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                description += sentence + ". "
                if (len(description) > 650):  #Once we exceed 700, dat's da last sentence
                    break
            readmore = artistweb #We had to cut it short, so you can read more at the event page UNLESS we found an artist link (in which case, go to their page)
        elif artistweb != newhtml:  #If description is short and we found an artist link (so artistweb is different than event page)
            readmore = artistweb #Have the readmore link provide more info about the artist
        else:
            readmore = "" #No artist link and short description - no need for readmore
        descriptionjammed = description.replace(" ","") # Create a string with no spaces
        try:
            ALLCAPS = re.findall("[A-Z]{15,}", descriptionjammed)[0] # If 15 or more sequential characters in the description are ALL CAPS, let's change the description!
            description = description.rstrip(".") # If there's a period at the end, get rid of it.
            separatesentences = description.split(".") #Let's split it into sentences!
            description = ""
            for onesentence in separatesentences:  #Let's rebuild, sentence-by-sentence!
                onesentence = onesentence.lstrip()  #Remove leading whitespace so that the capitalization works properly
                description += onesentence.capitalize() + ". "  #Capitalize ONLY the first letter of each sentence - if proper names aren't capitalized or acronyms become faulty, then that's their fault for abusing ALL CAPS
        except:
            aintnobigthang = True # placeholder code (No excessive ALL CAPS abuse found)
        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"]
        except:
            print("Could not find ticket link for", newhtml)
            pages.add(newPage)
            pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
            continue
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
        try:   
            artistpic = bsObj.find("div", {"class":"event-detail"}).find("img").attrs["src"]
        except:
            artistpic = ""
        miracletest = bsObj.findAll("title")[0].get_text()
        if "Miracle Theatre" in miracletest:
            venuelink = "http://themiracletheatre.com/"
            venuename = "Miracle Theatre"
            addressurl = "https://goo.gl/maps/62b4LRVB4uP2"
            venueaddress = "535 8th St. SE, Washington, DC 20003"
        else:
            venuelink = "https://www.unionstage.com/"
            venuename = "Union Stage"
            addressurl = "https://goo.gl/maps/p5Jm72L1VVA2"
            venueaddress = "740 Water St SW, Washington, DC 20024"
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
        print(newhtml)
csvFile.close()
backupCSV.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/unionusedlinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-union.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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