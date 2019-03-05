#Scrapes Rock and Roll Hotel's events, using - http://www.rockandrollhoteldc.com/  
#DO, FUTURE - figure out system for genre and local, store photo and video links, artist music link?

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
    with open('../scraped/usedlinks-rockhotel.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Dates in table are 2017-12-16 format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
            if dadate.date() >= today:  #If previoiusly-scraped event is in future...
                try:  # Check to make sure that previously scraped events are still valid
                    diditwork = urlopen(line[0])
                except:
                    print(line[1], " - ", line[0],"caused an error...")
    previousscrape.close()

counter = 0  #to keep track of progress while program running
UTFcounter = 0

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "http://www.rockandrollhoteldc.com/"
venuename = "Rock & Roll Hotel"
addressurl = "https://goo.gl/maps/PNCN25D5p4q"
venueaddress = "1353 H St. NE, Washington, DC 20002"

csvFile = open('../scraped/scraped-rockhotel.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/RockHotelScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://www.rockandrollhoteldc.com/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(http\:\/\/www\.rockandrollhoteldc\.com\/calendar\/)")): #The link to each unique event page begins with "http://www.rockandrollhoteldc.com/calendar/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        if "trivia-night" in newPage:
            continue
        newhtml = newPage
        html = urlopen(newhtml)
        print(newhtml)
        bsObj = BeautifulSoup(html)
        try:
            price = bsObj.find("div", {"class":"info_right"}).get_text() # Pulls the price, which could be a price range, plus bonus text.  MIGHT BE SOLD OUT
        except:
            print("Could not find price for ", newhtml, " - skipped it.")
            continue
        if "SOLD" in price or "Sold" in price or "sold" in price: # Don't bother with event if it's sold out
            continue
        if "FREE" in price or "Free" in price or "free" in price:
            price = "FREE!"
        prices = re.findall("[0-9]{1,3}", price)
        try:
            if (prices[0] == prices[1]):
                price = "$" + prices[0]
            else:
                price = price.strip() # Get rid of beginning and ending carriage returns
                price = price.replace("|","- ")
                price = price.replace("\n","| ") # Eliminates annoying middle carriage return
                price = price.replace("\r","| ") # Eliminates annoying middle carriage return
        except:
            fakevariable = 3 # damn try won't work without an except, even though I need no except
        try:
            datelong = bsObj.find("div", {"class":"artist_date-single"}).get_text() # This includes the day of the week and (usually? always?) additional text re: age restrictions
        except:
            datelong = bsObj.find("div", {"class":"artist_date"}).get_text() # This includes the day of the week and (usually? always?) additional text re: age restrictions
        try:
            dadate = re.findall("[A-Za-z]{3}\s+[A-Za-z]{3}\s+[0-9]{1,2}", datelong)[0]
        except:
            dadate = re.findall("[A-Za-z]{3}\.\s+[A-Za-z]{3}\s+[0-9]{1,2}", datelong)[0]  # MIGHT have a period after the day of the week
        dadate = dadate.replace(".","")  # Get rid of period if it exists
        year = today.year
        date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%a %b %d %Y').date()
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year 
            date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%a %b %d %Y').date()
        if date > today + datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        starttime = bsObj.find("div", {"class":"date_right"}).get_text() # Pulls time, including pm (spreadsheet doesn't care about that)
        artist = bsObj.find("div", {"class":"artist_title_opener_single"}).get_text().strip() # Event name
        if artist.lower() == "closed" or "TOASTY BINGO" in artist.upper() or "TRIVIA NIGHT" in artist.upper():
            continue
        artist = artist.replace("SUMMIT","Summit")
        try:
            artistweb = bsObj.find("div", {"class":"music_links"}).find("a").attrs["href"]  #THIS finds the first instance of a div with a class of "music_links", then digs deeper, finding the first instance w/in that div of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = newhtml
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"artist_content"}).get_text().strip() # Get the description.
        except:
            description = ""
        description = re.sub(r'TICKETS\sON[\s\-]SALE\s[A-Z]+DAY\s[A-Z]+\s[0-9]{1,2}[A-Z]{2}\s\@\s[0-9]{1,2}[AP]M', '', description)
        description = description.replace("TICKETS ON SALE NOW","")
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        description = description.replace("FREE | EVERY SATURDAY NIGHT | MAIN ROOM (1ST FLOOR) | 21+ | 11:30 pm – close","") # Get rid of annoying crap
        description = description.replace("SUMMIT","Summit")
        description = description.replace("DJ BASSCAMP PRESENTS","DJ Basscamp Presents")
        description = description.replace("RESIDENT","resident")
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
        try:
            ticketweb = bsObj.find("div", {"class":"ticket_btn"}).find("a").attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door or free
        except:
            print("Didn't find ticket sales for ", newhtml)
            ticketweb = ""
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
        if len(description) > 100 and "Summit Saturdays" not in artist and "TRIBUTE" not in artist and "Tribute" not in artist:  #Some things are not worthy of a picture
            try:   
                artistpic = bsObj.find("div", {"class":"artist-thumbnail-large"}).find("img").attrs["src"]
            except:
                artistpic = ""
        else:
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
                try:
                    writer.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    print("Using UTF encoding for artist and description", date)
                except:
                    writer.writerow((date, genre, "", local, doors, price, starttime, newhtml.encode('UTF-8'), artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    backupwriter.writerow((date, genre, "", local, doors, price, starttime, newhtml.encode('UTF-8'), artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    print("Using UTF encoding for artist and description AND EVENT URL", date)
        pages.add(newPage)
        pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
csvFile.close()
backupCSV.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/RockandRollUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-rockhotel.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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