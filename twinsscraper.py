
from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-twins.csv'
dateFormat = '%Y-%m-%d'
numDays = 30
linkCheckUrl = "https://www.instantseats.com/"

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)


UTFcounter = 0

genre = "Jazz & Blues"  
venuelink = "http://www.twinsjazz.com/"
venuename = "Twins Jazz"
addressurl = "https://goo.gl/maps/cs58EnKHujN2"
venueaddress = "1344 U St. NW, Washington, DC 20009"
musicurl = ""
doors = " "

localList = scraperLibrary.getLocalList()

fileName = '../scraped/scraped-twins.csv'
backupFileName = '../scraped/BackupFiles/TwinsScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


html = urlopen("http://www.instantseats.com/index.cfm?fuseaction=home.venue&venueid=10")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(index\.cfm\?fuseaction\=home\.event)")): #The link to each unique event page begins with "index.cfm?fuseaction=home.event"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "https://www.instantseats.com/" + newPage
        print(newhtml)
        html = urlopen(newhtml)
        bsObj = BeautifulSoup(html)
        datelong = bsObj.find("span", {"class":"start-time"}).get_text()  # This pulls out all of the text - the day of the week, the date, the start time, and the price. Need to extract the date, time, and cost.
        dateonly = re.findall(",\s([a-zA-Z]+\s[0-9]+)", datelong)[0] #This pulls out the date
        #dateonly = dateonly.replace("\n"," ") # Eliminates annoying carriage returns, if any
        #dateonly = dateonly.replace("\r"," ") # Eliminates annoying carriage returns, if any
        year = today.year
        print(dateonly)
        dadate = datetime.datetime.strptime((dateonly.strip() + ' ' + str(year)), '%B %d %Y').date() 
        if dadate < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year
            dadate = datetime.datetime.strptime((dateonly.strip() + ' ' + str(year + 1)), '%B %d %Y').date()
        if dadate > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!):
            continue
        starttime = str(int(re.findall("[\n\r]([0-9]+)", datelong)[0])+12)+":00" #This extracts the number portion of the time, converts it to an integer, adds 12 ('cuz all Twins events in eve), converts to a string, and adds :00.
        if "free" in datelong.lower():
            price = 0
        else:
            price = re.findall("\$[0-9]+", datelong)[0]  #This extracts the ticket price
        artistname = bsObj.find("h2", {"class":"artist-name"}).get_text() #This gets the artist's name
        if len(artistname) > 6:
            words = artistname.split()  #The artist name may be ALL CAPS, so if it's more than 6 characters, we're converting it to proper capitalization
            artist = ""
            firstword = True
            for splat in words:  #De-capitalize the artist name
                if (firstword == False and splat.lower() in ("the", "a", "an", "of", "and", "but", "or", "for", "nor", "to", "on", "at", "from")):
                    artist += splat.lower() + " "
                    firstword = False
                else:
                    artist += splat.capitalize() + " "
                    firstword = False
        else:
            artist = artistname
        artist = artist.strip() 
        if compactWord(artist) in locallist:
            local = "Yes"
        else:
            local = ""
        descriptionparagraphs = list(bsObj.find("p", {"class":"description"}).next_siblings) # Gets the description.  NOTE 1 - be wary of multiple paragraphs with class of "Description"!!!!  NOTE 2 - funky paragraph structure required accessing the siblings rather than getting the description directly.
        description = "" #Create an empty string
        counter = 0  #Need to create a loop in order to be able to use the .get_text thingie
        while (counter < len(descriptionparagraphs)):
            try: #The content (or lack thereof) of some paragraphs cause fatal errors
                textblob = descriptionparagraphs[counter].get_text().strip()
                counter += 1
                if "$" in textblob and "cover" in textblob:
                    continue
                description += textblob + " \u00A4 "  # Description may be split between multiple paragraphs.  A symbol is concatenated in case, say, the site lists each musician in a separate paragraph.
            except:
                counter += 1
        description = description.replace("Visit Website"," ")
        description = description.replace(" \u00A4   \u00A4 "," \u00A4 ") # In case symbol occurs two times in a row, separated by space &nbsp; space
        description = description.replace(" \u00A4   \u00A4 "," \u00A4 ") # In case symbol occurs two times in a row, separated by space space space
        description = description.strip()
        description = description.strip("\u00A4")
        description = description.strip()
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        if (len(description) > 700): # If the description is too long...
            descriptionsentences = description.split(". ") #Let's split it into sentences!
            description = ""
            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                description += sentence + ". "
                if (len(description) > 650):  #Once we exceed 700, dat's da last sentence
                    break
            readmore = newhtml #We had to cut it short, so you can read more at the event page
        else:
            readmore = "" #We included the full description, so no need to have a readmore link
        artistweb = newhtml
        ticketweb = newhtml
        alldalinks = bsObj.findAll("a")
        musicurl = ""
        for onelink in alldalinks:
            try:
                if "youtube" in onelink.attrs["href"]:
                    musicurl = onelink.attrs["href"]
                    break
            except:
                continue
        artistpic = ""
        alldapics = bsObj.findAll("img")
        if starttime != "22:00" and starttime != "23:00":  #Pulls photo from site IF not the late show (only want pics for one show per day)
            for onepic in alldapics:
                if ".jpg" in onepic.attrs["src"]:
                    artistpic = "https://www.instantseats.com" + onepic.attrs["src"]
                    break
        try:  # Might crash with weird characters.
            writer.writerow((dadate, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
            backupwriter.writerow((dadate, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
        except:
            UTFcounter += 1
            try:
                writer.writerow((dadate, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((dadate, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                print("Using UTF encoding for description", dadate)
            except:
                writer.writerow((dadate, genre, artistpic, local, doors, price, starttime, artistweb, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((dadatey, genre, artistpic, local, doors, price, starttime, artistweb, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                print("Using UTF encoding for artist and description", dadate)
        pages.add(newPage)
        pageanddate.add((newPage,dadate,datetoday))  # Add link to list, paired with event date and today's date
csvFile.close()
backupCSV.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/TwinsUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-twins.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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