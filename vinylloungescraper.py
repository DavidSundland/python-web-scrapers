#Scrapes Gypsy Sally's events, using - http://www.gypsysallys.com/calendar/  


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
    answer = input("Do you want to open used links files? (Skip previously-used links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-vinyl.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        try:
            dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Newer dates in table are 2017-12-16 format.
        except:
            dadate = datetime.datetime.strptime((line[1].strip()), '%a, %B %d, %Y') #Date in table is in d.o.w.(abbrev.), month day, year format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
            testhtml = "http://www.gypsysallys.com" + line[0]
            try:
                diditwork = urlopen(testhtml)
            except:
                print(testhtml,"caused an error...")
    previousscrape.close()
    
    # Pulls events from other part of Gypsy Sally's site; no longer needed?:
    
#    with open('../scraped/usedlinks-gypsy.csv', 'r') as previousgypsy: 
#        reader = csv.reader(previousgypsy)
#        previousinfo = list(reader)
#    for line in previousinfo:
#        dadate = datetime.datetime.strptime((line[1].strip()), '%a, %B %d, %Y') #Date in table is in d.o.w.(abbrev.), month day, year format.
#        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
#            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
#            pages.add(line[0])
#    previousgypsy.close()

counter = 0 # A counter to track progress
UTFcounter = 0 # Counter for number of encoding problems

price = "Free!"
artistpic = ""
doors = " "
venuelink = "http://www.gypsysallys.com/"
venuename = "Gypsy Sally's"
addressurl = "https://goo.gl/maps/omk3qVuLwWG2"
venueaddress = "3401 Water St. NW, Washington, DC 20007"

csvFile = open('../scraped/scraped-vinyl.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/VinylLoungeScraped" + datetoday + ".csv"
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCVS)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.gypsysallys.com/vinyl-lounge-listing/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "http://www.gypsysallys.com" + newPage
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        genre = "Americana"  # Add test for genre in future
        local = ""  # Add test for local in future
        date = bsObj.find("h2", {"class":"dates"}).get_text() # This includes the day of the week, the year and, sometimes, extra spaces.  The spreadsheet doesn't care. (Including year good for E.O.Y.)
        dadate = datetime.datetime.strptime((date.strip()), '%a, %B %d, %Y') #Date in table is in day month day, year format.
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
            continue
        time = bsObj.find("span", {"class":"dtstart"}).get_text() # Pulls time, including pm (spreadsheet doesn't care about that) AND "Show:" (NOTE - also has class name of "start")
        starttime = re.findall("[0-9]{1,2}:[0-9]{2}\s*[aApP][mM]", time)[0] #This extracts the time, including am/pm
        artist = bsObj.find("h1", {"class":"headliners summary"}).get_text() # Event / top artist name
        artist = artist.replace("VINYL LOUNGE OPEN MIC", "Vinyl Lounge Open Mic") # Eliminate annoying all-caps, if applicable
        artist = artist.replace(", VINYL LOUNGE", "") # Eliminate 'bonus' info about artist being @ Vinyl
        if "CLOSED" in artist or "closed" in artist or "Closed" in artist or "private event" in artist or "Private Event" in artist or "PRIVATE EVENT" in artist: # Skip closed private events
            continue
        if "Open Mic" in artist:
            genre = "Potpourri"
            local = "Yes"
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = newhtml
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"bio"}).get_text() # Get the description, which does include a lot of breaks - will it be a mess?
        except:
            description = ""
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        if (len(description) > 700): # If the description is too long...  
            descriptionsentences = description.split(". ") #Let's split it into sentences!
            description = ""
            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                description += sentence + ". "
                if (len(description) > 650):  #Once we exceed 650, dat's da last sentence
                    break
            readmore = artistweb #We had to cut it short, so you can read more at the event page UNLESS we found an artist link (in which case, go to their page)
        elif artistweb != newhtml:  #If description is short and we found an artist link (so artistweb is different than event page)
            readmore = artistweb #Have the readmore link provide more info about the artist
        else:
            readmore = "" #No artist link and short description - no need for readmore
        descriptionjammed = description.replace(" ","") # Create a string with no spaces
        try:
            ALLCAPS = re.findall("[A-Z]{10,}", descriptionjammed)[0] # If 10 or more sequential characters in the description are ALL CAPS, let's change the description!
            description = description.rstrip(".") # If there's a period at the end, get rid of it.
            separatesentences = description.split(".") #Let's split it into sentences!
            description = ""
            for onesentence in separatesentences:  #Let's rebuild, sentence-by-sentence!
                onesentence = onesentence.lstrip()  #Remove leading whitespace so that the capitalization works properly
                description += onesentence.capitalize() + ". "  #Capitalize ONLY the first letter of each sentence - if proper names aren't capitalized or acronyms become faulty, then that's their fault for abusing ALL CAPS
        except:
            aintnobigthang = True # placeholder code (No excessive ALL CAPS abuse found)
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
            fakevariable = "kibbles"
        ticketweb = ""
        try:
            ticketwad = bsObj.find("h3", {"class":"price-range"}).find_next_siblings()  #Ticket link not uniquely labeled - links to tickets to OTHER events have same labels as page's event...
            for brosis in ticketwad:
                try:
                    ticketweb = brosis.find("a", {"class":"tickets"}).attrs["href"]  #Event's ticket link (if applicable) is in one of the siblings to "price-range"
                except:
                    continue
        except:
            fakevariable = "nbitsnbitsnbits"
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
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/VinylLoungeUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-vinyl.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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
