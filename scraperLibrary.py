#Scrapes 9:30 Club's concerts

from urllib.request import urlopen #for pulling info from websites

import requests  # due to changes in site's encoding, needed to add this import

from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime


#description: string; deleteItems: array of items to delete from description (may be unique to each venue)
def descriptionTrim(description, deleteItems, numChars, artistWeb, newHtml):
    description = description.replace("\n"," ").replace("\r"," ") # Eliminates annoying carriage returns 
    for item in deleteItems:
        description = description.replace(item,"")
    splitChars = [". ","! ","? ",".' ",'." ']
    pointer = 0
    while len(description) > numChars and pointer <= 4: # If the description is too long...
        [description, readmore] = descriptionSplit(description, splitChars[pointer], numChars, artistWeb)
        pointer += 1
    if pointer > 0 and artistweb != newhtml:  #If description is short but we found an artist link
        readmore = artistweb #Have the readmore link provide more info about the artist
    else if pointer > 0:
        readmore = "" #No artist link and short description - no need for readmore
    return [description, readmore]

def descriptionSplit(description, splitChar, numChars, artistWeb):
    descriptionsentences = description.split(splitChar) #Let's split it into sentences!
    description = ""
    for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
        description += sentence + splitChar
        if (len(description) > numChars-50):  #Once we get close to max, dat's da last sentence
            break
    readmore = artistWeb #We had to cut it short, so you can read more at the event or artist page
    return [description, readmore]
    



pages = set() #create an empty set of pages
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you open used links file? (Avoid scraping previously scraped links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-930.csv', 'r') as previousscrape:
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        try:
            dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Newer dates in table are 2017-12-16 format.
        except:
            try:
                dadate = datetime.datetime.strptime(line[1].strip(), '%a %m/%d/%y') #Date in table used to be in day of week (abbrev) month/day/year format.
            except:
                try:
                    dadate = datetime.datetime.strptime(line[1].strip() + ' 2017', '%a, %B %d %Y')    #Date format changed to Fri, June 30 in 2017.  (2017 remnants exist w/o year)
                except:
                    dadate = datetime.datetime.strptime(line[1].strip(), '%a, %B %d %Y')  # This SHOULD be the format for events moving forward
        if dadate.date() > today-datetime.timedelta(days=90):  #If used link is NOT something that was scraped more than 3 months ago, add it to list\
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

counter = 0
UTFcounter = 0 # Counter for number of encoding problems

local = ""
genre = "Rock & Pop"
doors = "Doors:"
venuelink = "http://www.930.com/"
venuename = "9:30 Club"
addressurl = "https://goo.gl/maps/EbAXTg6iEvE2"
venueaddress = "815 V St. NW, Washington, DC 20001"

datetoday = str(today)
backupfile = "../scraped/backupfiles/930Scraped" + datetoday + ".csv"
csvFile = open('../scraped/scraped-930.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
writer = csv.writer(csvFile)
backupwriter = csv.writer(backupCVS)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))


# html = urlopen("https://www.930.com/#upcoming-shows-container")  # due to changes in site's encoding, this no longer works
# html = urlopen("http://www.930.com/")
# firstBS = BeautifulSoup(html)

html = "https://www.930.com/#upcoming-shows-container"
firstBS = BeautifulSoup(requests.get(html).text)

print("got initial bs; bs: ", firstBS)
for link in firstBS.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    print(newPage)
    if newPage not in pages: #A new link has been found
        counter += 1
        newhtml = "https://www.930.com" + newPage
        print("got newhtml:", newhtml)
#        html = urlopen(newhtml)  # due to changes in site's encoding, this no longer works
        bsObj = BeautifulSoup(requests.get(newhtml).text)
        # print("BSed:",newhtml) # To track progress and for debugging purposes
        dateonly = bsObj.find("h2", {"class":"dates"}).get_text() # This is now in "Fri, June 30" format (no year!)
        year = today.year
        date = datetime.datetime.strptime((dateonly.strip() + ' ' + str(year)), '%a, %B %d %Y').date()  # Added year (initially assume current year)
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
            date = datetime.datetime.strptime((dateonly.strip() + ' ' + str(year + 1)), '%a, %B %d %Y').date()
        if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
            continue
        ustreettest = bsObj.find("title").get_text() # Pulls the title...
        if "U Street" in ustreettest: # If U Street is in the title, it's off-site, so skip
            continue
        try:  # hit issue one time where "doors" not included and time not in "doors" class
            time = bsObj.find("span", {"class":"doors"}).get_text() # Pulls time, including pm (spreadsheet doesn't care about that) AND "Doors:"
            starttime = re.findall(".+:\s+([0-9]+:[0-9]{2}\s*[ap]m)", time)[0] #This extracts the time, including am/pm
        except: 
            time = bsObj.find("span", {"class":"start"}).get_text().strip()  #No extraneous info in this'un
            doors = ""  #Shows actual start time, not doors open time
        price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range
        try:  # Hopefully if this info is missing, it's cuz not yet in site, not because of scraping error
            artist = bsObj.find("span", {"class":"artist-name"}).get_text() # Event / top artist name  NOTE - "div" of "artist-headline" also an option
        except:
            try:
                artist = bsObj.find("h1", {"class":"headliners"}).get_text() # Event / top artist name
            except:
                print("Skipped", date, time)
                continue
        try:
            musicurl = bsObj.find("iframe").attrs["src"] # If there's a video, grab it and toss it into the "buy music" column
        except:
            musicurl = ""
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = newhtml
        description = artist.rstrip('.') + ". " # Start description with artist name and period (first remove a period if it exists to avoid double periods)
        try:
            description += "With: " + bsObj.find("h2", {"class":"supports description"}).get_text() + ". " # Adds supporting artists (or additional title info)
        except:
            description = ""  # If supporting artists aren't listed, don't bother starting description with headliner.
        for eachartist in bsObj.findAll("div", {"class":"bio"}):  #NOTE - pulls descriptions for all artists (in case 1st artist has no description)
            try: # There isn't always a description...
                description += eachartist.get_text() + " " # Get the description, which does include a lot of breaks - will it be a mess?
            except:
                description = description
#        try: # There isn't always a description...
#            description = bsObj.find("div", {"class":"bio"}).get_text() # Get the description, which does include a lot of breaks - will it be a mess?
#        except:
#            description = ""
        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door
        except:
            ticketweb = ""
        artistpic = ""
        try:
            allimages = bsObj.findAll("img") 
            for oneimage in allimages:
                if "ticketfly" in oneimage.attrs["src"] and ".jpg" in oneimage.attrs["src"]:
                    artistpic = oneimage.attrs["src"]
                    break
        except:
            howcanthisbe = "no images?"
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
        print(newhtml, date)
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/backupfiles/930usedlinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-930.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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
