#Scrapes Dangerous Pie's events, using - http://pieshopdc.com/events/  

from urllib.request import urlopen #for pulling info from websites
import requests  # if urllib doesn't work
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping

def split(txt, seps):
    default_sep = seps[0]

    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

usedLinksFile = '../scraped/usedlinks-dangerous.csv'
dateFormat = '%m/%d/%Y'
numDays = 30
linkCheckUrl = True

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)

UTFcounter = 0

doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "http://www.dangerouspiesdc.com/"
venuename = "Dangerous Pies"
addressurl = "https://goo.gl/maps/N22YNxAXZxx"
venueaddress = "1339 H St NE, Washington, DC 20002"

csvFile = open('../scraped/scraped-dangerous.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "../scraped/BackupFiles/PearlScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

#html = urlopen("http://pieshopdc.com/events/")
bsObj = BeautifulSoup(requests.get("http://pieshopdc.com/events/").text)
print(bsObj)
for link in bsObj.findAll("a",href=re.compile("^(https\:\/\/pieshopdc\.com\/events\/)")): #The link to each unique event page begins with "https://pieshopdc.com/events/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = newPage
        print(newhtml)
#        html = urlopen(newhtml)
#        bsObj = BeautifulSoup(html)
        bsObj = BeautifulSoup(requests.get(newhtml).text)
        price = bsObj.find("div", {"class":"eventCost"}).get_text().strip() # Pulls the price
        datelong = bsObj.find("span", {"class":"eventStDate"}).get_text() # This includes the day of the week, but no year
        dadate = re.findall("[JFMASOND][a-z]+\s[0-9]{1,2}", datelong)[0]
        year = today.year
        date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year)), '%M %d %Y').date()
        if date < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year 
            date = datetime.datetime.strptime((dadate.strip() + ' ' + str(year + 1)), '%M %d %Y').date()
        if date > today + datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        timelong = bsObj.find("div", {"class":"eventDoorStartDate"}).get_text()
        time = re.findall("[0-9]{1,2}\s*[pPaA][mM]")[0]
        artist = bsObj.find("title").get_text().strip() # Event name
        artist = re.sub("\s\-\s+(pie\sshop)(?i)","",artist)
        content = bsObj.find("div", {"class":"singleEventDescription"}).get_text()
        links = re.findall('http\S+',content)
        if len(links) > 1:
            description = split(content,links)[1:].join(' ')
            artistweb = links[0]
        elif len(links) == 1:
            description = content.split(links[0])[1]
            artistweb = links[0]
        else:
            description = content
            artistweb = ""

        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)
        
        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)

        try:
            ticketurl = bsObj.find("a", {"title":"Buy Tickets"}).attrs["href"]
        except:
            print("Could not find ticket link for", newhtml)
            ticketurl = ""
        musicurl = ""
        try:   
            artistpic = bsObj.find("img", {"class":"wp-post-image"}).attrs["src"]
        except:
            artistpic = ""
        localList = scraperLibrary.getLocalList()
        if scraperLibrary.compactWord(artist) in localList:
            local = "Yes"
        else:
            local = ""

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
    linksBackup = "../scraped/BackupFiles/DangerousUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-dangerous.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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