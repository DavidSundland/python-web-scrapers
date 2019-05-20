#Scrapes DC9's events, using - http://dcnine.com/calendar/  

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
    answer = input("Do you want to open used links file? (Skip previously-used links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-dc9.csv', 'r') as previousscrape:  
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%m/%d/%Y') #Date in table is now in 4/28/2018 format
        if dadate.date() > today-datetime.timedelta(days=30):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

counter = 0  #to keep track of progress while program running
UTFcounter = 0

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "https://www.dc9.club/"
venuename = "DC9"
addressurl = "https://goo.gl/maps/Vnzq6cjvcjv"
venueaddress = "1940 9th St. NW, Washington, DC 20001"
musicurl = ""

csvFile = open('../scraped/scraped-dc9.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/backupfiles/DC9Scraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("https://dc9.club/calendar/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with /event/
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
#        counter += 1
        newhtml = "https://www.dc9.club" + newPage
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        datelongest = bsObj.find("span", {"class":"value-title"}).attrs["title"]
        datelonger = re.findall("20[12][0-9]\-[0-2][0-9]\-[0-3][0-9]T[0-9]{2}\:[0-9]{2}\:[0-9]{2}", datelongest)[0]
        datelong = datetime.datetime.strptime(datelonger, "%Y-%m-%dT%H:%M:%S")
        date = str(datelong.month) + "/" + str(datelong.day) + "/" + str(datelong.year)
        starttime = str(datelong.time())
        year = today.year
        if datelong.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        try:
            price = bsObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range...
        except:
            price = "Free!"  # In the first instance in which price-range failed, event was free...
            print("Verify that ", newhtml, " is indeed free!!!!!!!")
        if "sold out" in price.lower():
            continue
        if "rsvp" in price.lower() and len(re.findall([0-9],price)) == 0:
            price = "Free!"
        artist = bsObj.find("h1", {"class":"headliners"}).get_text().strip() # Event name

        skippers = ["sold out","mixtape","peach pit","karaoke","liberation dance party","astronomy on tap","nerd nite","90s tracks","wig & disco","daft lunch","dark & stormy","show moving to","closed for private event","vinyl head"]
        skip = False
        for skipper in skippers:
            if skipper in artist.lower():
                skip = True
        if skip:
            continue
        artist = re.sub('\s\[\s*[eE][aA][rR][lL][yY]\s+[sS][hH][oO][wW]\s*\]','',artist)
        artist = re.sub('\s\[\s*[lL][aA][tT][eE]\s+[sS][hH][oO][wW]\s*\]','',artist)
        artist = re.sub('\s\[\s*[eE][aA][rR][lL][yY]\s+[eE][vV][eE][nN][tT]\s*\]','',artist)
        artist = re.sub('\s\[\s*[lL][aA][tT][eE]\s+[eE][vV][eE][nN][tT]\s*\]','',artist)
        if len(re.findall("[A-Z]", artist)) > 8 and len(re.findall("[a-z]", artist)) < 4: # if caps are abused...
            artist = scraperLibrary.titleCase(artist)
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            try:
                artistweb = bsObj.find("li", {"class":"facebook"}).find("a").attrs["href"]
            except:
                artistweb = ""
        try:
            description = bsObj.find("div", {"class":"bio"}).get_text().strip()
        except:
            description = ""
            print("Found no description")
        description = description.replace("  / ","").strip("/").strip().strip("/").strip()
        description = re.sub('((Tickets\s)|(TICKETS\s))([gG][oO]\s)*((on[\s\-]sale\s)|(ON[\s\-]SALE\s))[A-Za-z]+\,*\s([0-9\/\-]{3,5}|([a-zA-Z]+)\s[0-9]{1,2})\s(\@|[aA][tT])\s(([0-9]{1,2}[aA][mM])|([nN][oO][oO][nN]))','',description)
        [description, readmore] = scraperLibrary.descriptionTrim(description, ["OFFICIAL WEBSITE","TWITTER","FACEBOOK"], 800, artistweb, newhtml)
        try:
            musicurl = bsObj.find("li", {"class":"soundcloud"}).find("a").attrs["href"]
        except:
            try:
                musicurl = bsObj.find("li", {"class":"bandcamp"}).find("a").attrs["href"]
            except:
                try:
                    iframes = eventObj.findAll("iframe") # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
                    for onei in iframes:  
                        if "youtube" in onei.attrs["src"]:
                            musicurl = onei.attrs["src"]
                            break  # Once first video is found, move along (don't take back-up band's video over headliner; don't have 'else' overwrite found link)
                        else:
                            musicurl = ""  # In case there are iframes, but no videos
                except: musicurl = ""
        artistpic = bsObj.find("img").attrs["src"]  #artist pic should be first img
        try:
            ticketweb = bsObj.find("a", {"class":"tickets"}).attrs["href"]
        except:
            print("Found no ticket link for ", newhtml)
            ticketweb = ""
#        for oneimage in images:
#            if "photobucket" in oneimage.attrs["src"]:
#                artistpic = oneimage.attrs["src"]
#                break
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
#        print(counter)
csvFile.close()
backupCSV.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/backupfiles/DC9UsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-dc9.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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