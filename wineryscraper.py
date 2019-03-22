#Scrapes City Winery events, using - https://citywinery.com/washingtondc/tickets.html?view=calendar&month=6&year=2018/  FOR SPREADSHEET, USE Scraping - Basic Sites



from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #regular expressions
import csv #comma-separated values
import datetime
from datetime import date # necessary for properly calculating time differences in months
from dateutil.relativedelta import relativedelta # necessary for properly calculating time differences in months

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-winery.csv'
dateFormat = '%m/%d/%y'
numDays = 30
linkCheckUrl = True

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)

UTFcounter = 0 # Counter for number of encoding problems (thusfar not needed for Blues Alley)

doors = " "
genre = "Rock & Pop"
venuelink = "https://citywinery.com/washingtondc/"
venuename = "City Winery"
addressurl = "https://goo.gl/maps/jhjUuxZ44sp"
venueaddress = "1350 Okie St NE, Washington, DC 20002"

fileName = '../scraped/scraped-winery.csv'
backupFileName = '../scraped/BackupFiles/WineryScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


# Scraping 1 month at a time, creating URL to match: https://citywinery.com/washingtondc/tickets.html?view=calendar&month=6&year=2018
for monthrange in range(0,2):  # look at this month & next; possibly look farther in future
    month = ((today+relativedelta(months=+monthrange)).strftime("%m")).lstrip("0")
    monthurl = "https://citywinery.com/washingtondc/tickets.html?view=calendar&month="  + month + "&year=" + (today+relativedelta(months=+monthrange)).strftime("%Y")
    html = urlopen(monthurl)
    bsObj = BeautifulSoup(html)
    for link in bsObj.findAll("a",href=re.compile(".+[01]?[0-9]\-[0-3]?[0-9]\-[12][0-9].+|.+[01][0-9][0-3][0-9][12][0-9].+")): #The link to each unique event page includes the event date in 6-29-18 format OR 062918 format
        newPage = link.attrs["href"] #extract the links
        if newPage not in pages: #A new link has been found
            pages.add(newPage)
            newhtml = newPage # An extra line of code; used 'cuz in some cases a site's base URL needs to be added to the internal link
            html = urlopen(newhtml)
            print(newPage)
            bsObj = BeautifulSoup(html)
            artistweb = newhtml
            musicurl = ""
            try:
                iframes = bsObj.findAll("iframe") # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
                for onei in iframes:  
                    if "soundcloud" in onei.attrs["src"]:
                        musicurl = onei.attrs["src"]
                        break  # If Soundcloud link found, snag it and quit
                    else:
                        if "youtube" in onei.attrs["src"]:
                            musicurl = onei.attrs["src"]
                            break  # Grab first video that comes along
                        else:
                            musicurl = ""  # In case there are iframes, but no videos
            except:
                musicurl = ""
            artistlong = bsObj.find("h1", {"class":"page-title"}).get_text().strip() #This gets the event name (including extra crap)
            artist = artistlong.split(" - ")[0].strip() # event name is 1st part of title, separated from date by " - "
            date = re.findall("[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{1,2}",artistlong)[0]
            localList = scraperLibrary.getLocalList()
            if scraperLibrary.compactWord(artist) in localList:
                local = "Yes"
            else:
                local = ""

            try:
                artistweb = bsObj.find("li", {"class":"website"}).find("a").attrs["href"]
            except:
                try:
                    artistweb = bsObj.find("li", {"class":"facebook"}).find("a").attrs["href"]
                except:
                    artistweb = ""
            pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
            longtime = bsObj.find("span", {"class":"event-date"}).get_text().strip()
            try:
                starttime = re.findall("([0-9]{1,2}\:[0-6][0-9]\s*[aApP][mM])\s*[sS][tT][aA][rR][tT]",longtime)[0]
            except:
                try:
                    starttime = re.findall("([0-9]{1,2}\s*[aApP][mM])\s*[sS][tT][aA][rR][tT]",longtime)[0]
                except:
                    print("Found no start time for above page, skipping.  Event name:", artist)
                    continue
            prices = bsObj.findAll("span", {"class":"price"})
            if len(prices) == 0:
                print("Found no price for above link, so skipping it.  Event name:", artist)
                continue  # Events with no price are non-music events (always? almost always?)
            else:
                maxprice=0
                minprice=10000
                for oneprice in prices:
                    oneticket = int(re.findall("([0-9]{1,2})\.[0-9]{2}",oneprice.get_text())[0])
                    if (oneticket < minprice):
                        minprice = oneticket
                    if (oneticket > maxprice):
                        maxprice = oneticket
                if (maxprice == minprice):
                    price = maxprice
                else:
                    price = "$" + str(minprice) + " to $" + str(maxprice)
            descriptionWad = bsObj.find("div", {"class":"value"})
            descriptionParagraphs = descriptionWad.findAll("p")
            description = ""
            for paragraph in descriptionParagraphs:
                if re.search("^\$[0-9]+",paragraph.get_text()): # get rid of paragraphs that merely provide pricing info
                    continue
                else:
                    description += paragraph.get_text() + " "

            if "must be 21 years of age" in description: # tasting events include this in description
                continue
                
            [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml) #U Street gets shorter descriptions
            
            artistpic = bsObj.find("p", {"class":"product-image"}).find("img").attrs["src"]
            ticketweb = newhtml
            write1 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb)
            write2 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
            write3 = (date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb)
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
csvFile.close()
backupCSV.close()

fileName = '../scraped/usedlinks-winery.csv'
backupFileName = '../scraped/BackupFiles/WineryUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")
