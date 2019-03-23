#Scrapes Rock and Roll Hotel's events, using - http://www.rockandrollhoteldc.com/  
#DO, FUTURE - figure out system for genre and local, store photo and video links, artist music link?

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-rockhotel.csv'
dateFormat = '%Y-%m-%d'
numDays = 30
linkCheckUrl = ""

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)


UTFcounter = 0

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"
venuelink = "http://www.rockandrollhoteldc.com/"
venuename = "Rock & Roll Hotel"
addressurl = "https://goo.gl/maps/PNCN25D5p4q"
venueaddress = "1353 H St. NE, Washington, DC 20002"

csvFile = open('../scraped/scraped-rockhotel.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
write0 = ("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL")
writer.writerow(write0)
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/RockHotelScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(write0)

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
        if "sold" in price.lower(): # Don't bother with event if it's sold out
            continue
        if "free" in price.lower():
            price = "FREE!"
        prices = re.findall("[0-9]{1,3}", price)
        if len(prices) > 1:
            if (prices[0] == prices[1]):
                price = "$" + prices[0]
            else:
                price = price.strip() # Get rid of beginning and ending carriage returns
                price = price.replace("|","- ")
                price = price.replace("\n","| ") # Eliminates annoying middle carriage return
                price = price.replace("\r","| ") # Eliminates annoying middle carriage return
        try:
            datelong = bsObj.find("div", {"class":"artist_date-single"}).get_text() # This includes the day of the week and (usually? always?) additional text re: age restrictions
        except:
            datelong = bsObj.find("div", {"class":"artist_date"}).get_text() # This includes the day of the week and (usually? always?) additional text re: age restrictions
        dadate = re.findall("[A-Za-z]{3}\.*\s+[A-Za-z]{3}\s+[0-9]{1,2}", datelong)[0].replace(".","")
        year = today.year
        date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%a %b %d %Y').date()
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year 
            date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%a %b %d %Y').date()
        if date > today + datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        starttime = bsObj.find("div", {"class":"date_right"}).get_text() # Pulls time, including pm (spreadsheet doesn't care about that)
        artist = bsObj.find("div", {"class":"artist_title_opener_single"}).get_text().strip() # Event name
        if artist.lower() == "closed" or "TOASTY BINGO" in artist.upper() or "TRIVIA NIGHT" in artist.upper() or "bring home the bacon" in artist.lower() or "dj bo" in artist.lower() or "bar open" in artist.lower():
            continue
        artist = artist.replace("SUMMIT","Summit")
        if len(re.findall('[A-Z]',artist)) >= 6 and len(re.findall('[A-Z]',artist)) >= len(artist)/2: #if CAPS are abused...
            artist = scraperLibrary.titleCase(artist)
        try:
            artistweb = bsObj.find("div", {"class":"music_links"}).find("a").attrs["href"]  #THIS finds the first instance of a div with a class of "music_links", then digs deeper, finding the first instance w/in that div of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = ""
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"artist_content"}).get_text().strip() # Get the description.
        except:
            description = ""
        description = re.sub('((Tickets\s)|(TICKETS\s))([gG][oO]\s)*((on[\s\-]sale\s)|(ON[\s\-]SALE\s))[A-Za-z]+\,*\s([0-9\/\-]{3,5}|([a-zA-Z]+)\s[0-9]{1,2})\s(\@|[aA][tT])\s(([0-9]{1,2}[aA][mM])|([nN][oO][oO][nN]))','',description)
        description = description.replace("SUMMIT","Summit")
        description = description.replace("DJ BASSCAMP PRESENTS","DJ Basscamp Presents")
        description = description.replace("RESIDENT","resident")

        [description, readmore] = scraperLibrary.descriptionTrim(description, ["TICKETS ON SALE NOW","FREE | EVERY SATURDAY NIGHT | MAIN ROOM (1ST FLOOR) | 21+ | 11:30 pm – close"], 800, artistweb, newhtml)

        try:
            ticketurl = bsObj.find("div", {"class":"ticket_btn"}).find("a").attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door or free
        except:
            print("Didn't find ticket sales for ", newhtml)
            ticketurl = ""
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

        write1 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketurl)
        write2 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl)
        write3 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl)
        
        try:  # Might crash with weird characters.
            writer.writerow(write1)
            backupwriter.writerow(write1)
        except:
            UTFcounter += 1
            try:
                writer.writerow(write2)
                backupwriter.writerow(write2)
                print("Using UTF encoding for description", date)
            except:
                writer.writerow(write3)
                backupwriter.writerow(write3)
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