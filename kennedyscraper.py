#Scrapes Kennedy Center events, but NOT MILLENNIUM STAGE.
# Future - add "Local" variable, adding in NSO, etc., automatically

from urllib.request import urlopen #for pulling info from websites
import requests #a substitute for urllib, which was not working on 3/19

from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


pages = set() #For list of used links
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""


while answer not in yesno:
    answer = input("Do you want to open used links file? (Skip previously-used links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-kennedy.csv', 'r') as previousscrape:  
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Date in table is in day of week, month day, year format. 
        if dadate.date() > today-datetime.timedelta(days=190):  #If used link is NOT something that was scraped more than 6 months ago, add it to list
            pageanddate.add((line[0],line[1]))  #Create list of links that have been checked before (NOTE - not adding event date, since can be range)
            pages.add(line[0])
    previousscrape.close()

UTFcounter = 0 # A counter to track times that UTF encoding necessary
genres = ("CHA", "CLA", "HOP", "OPR", "JAZ", "POP", "VOC", "FES")

doors = " "
venuelink = "http://www.kennedy-center.org"
venuename = "Kennedy Center"
addressurl = "https://goo.gl/maps/1WXUMkf2BVC2"
venueaddress = "2700 F St. NW, Washington, DC 20566"
musicurl = ""   #Add test for this in future?

ticketpages = set() #create an empty set of pages for ticket links

datetoday = str(today)
backupfile = "../scraped/BackupFiles/KennedyScraped" + datetoday + ".csv"
csvFile = open('../scraped/scraped-kennedy.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
writer = csv.writer(csvFile)
backupwriter = csv.writer(backupCVS)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

for genrecat in genres:
    url = "http://www.kennedy-center.org/calendar/genre/" + genrecat
    try: #did not work on 3/19
        html = urlopen(url)
        bsObj = BeautifulSoup(html)
    except:
        bsObj = BeautifulSoup(requests.get(url).text)
    for link in bsObj.findAll("a", href = re.compile("^(\/calendar\/event\/)")):
        newPage = link.attrs["href"] #extract the link
        newPage = newPage.strip("#tickets")  # Some links jump to ticket portion of page - delete this to avoid redundancies
        if newPage not in pages:
            newhtml = "http://www.kennedy-center.org" + newPage
            print(newhtml)
            try:
                eventhtml = urlopen(newhtml)
                eventObj = BeautifulSoup(eventhtml)
            except:
                eventObj = BeautifulSoup(requests.get(newhtml).text)
            artistweb = ""
            year = today.year
            datelong = eventObj.find("h2", {"class":"event-date"}).get_text().strip()
            date = re.findall("[JFMASOND][a-z]+\s+[0-9]{1,2}\,\s+20[12][0-9]", datelong)[0]
            dadate = datetime.datetime.strptime(date.strip(), '%B %d, %Y') #Date is in "March 16, 2017" format.
            if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it (a lot can happen in 2 months):
                break #Kennedy scrapes slowly; events always chronological, so when 2 months passed, can move on to next genre
            time = re.findall("[0-9]{1,2}\:[0-9]{2}\s+[aApP][mM]", datelong) # Extracts the time (should have one or no results)
            if time == []: # if no time results, then must have multiple time and/or date options.  ADD DATE AND TIME MANUALLY AFTER FILE CREATED!!!!
                starttime = newhtml + "#tickets"  #put link to tickets in file to make dates and times easier to manually extract
                ############## INVESTIGATE SELENIUM TO GET AROUND ISSUE OF DYNAMICALLY-GENERATED DATES & TIMES FOR CONCERT SERIES ###########%%%%%%%%******
                ## https://coderwall.com/p/vivfza/fetch-dynamic-web-pages-with-selenium ##
            else:
                starttime = time[0]
            if (genrecat == "CHA" or genrecat == "CLA" or genrecat == "VOC" or genrecat == "OPR"):
                genre = "Classical"
            elif (genrecat == "HOP" or genrecat == "POP"):
                genre = "Rock & Pop"
            elif (genrecat == "JAZ"):
                genre = "Jazz & Blues"
            else:
                genre = "Potpourri"
            artist = eventObj.find("h1", {"class":"event-title"}).get_text().strip() #Event title / artist name
            if artist == "":
                artist = eventObj.find("h1", {"class":"event-title"}).find_next_siblings()[0].get_text().strip()
            if "at Wolf Trap" in artist:  # Annoyingly, off-site events sometimes listed
                continue
            artist = artist.replace("SHIFT ","SHIFT: ")
            artist = artist.replace("National Symphony Orchestra","NSO")
            artist = re.sub("(Washington\sPerforming\sArts\s)[pP](resents)\:*\s+","",artist)
            artist = artist.replace("Young Concert Artists Presents ", "")
            artist = artist.replace("KC Jazz Club: ", "")
            artist = artist.replace("The Choral Arts Society of Washington presents:", "Choral Arts Society:")
            artist = re.sub("Vocal\sArts\sDC\s[pP]resents\:*\s+","",artist)
            artist = artist.replace("Fortas Chamber Music Concerts: ", "")
            artist = re.sub("(The\s)*(Washington\sChorus\s)[pP](resents)\:*\s+","Washington Chorus:",artist)
            if "NSO" in artist or "Washington National Opera" in artist or "Washington Chorus" in artist or "Choral Arts Society" in artist:
                local = "Yes"
            else:
                local = ""
            try:
                pricelong = eventObj.find("div", {"class":"price"}).get_text() #Price range IF not free ("price" class may not exist for free events)
            except:
#                print("Is",newhtml,"free?")  #Perhaps add this back in future - was creating false positives with events that were so far out they were skipped anyway
                pricelong = "See event link for pricing"
            if "free" in pricelong or "Free" in pricelong or "FREE" in pricelong:
                price = "Free!"
                ticketurl = ""
            elif "$" not in pricelong:
                price = "See event link for pricing"
                ticketurl = ""
            else:
                price = pricelong.replace("Price","")
                price = price.strip()
                ticketurl = newhtml + "#tickets"
            description = eventObj.find("div", {"class":"blurbpadding"}).get_text(' ').strip()
            description = description.strip()
            description = re.sub(r'\~+', '~~~', description) # Trim line break when included 

            [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml)

            artistpic = ""
            try:
                alldapics = eventObj.findAll("img")
                for oneimage in alldapics:
                    if "large_thumb" in oneimage.attrs["src"] or "event-images" in oneimage.attrs["src"]:
                        artistpic = oneimage.attrs["src"]
                        break
            except:
                artistpic = ""
            if "default-480" in artistpic: #Get rid of default image of Kennedy Center
                artistpic = ""
            pages.add(newPage)
            pageanddate.add((newPage,datetoday))  # Add link to list, paired with today's date
            
            write1 = (date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketurl)
            write2 = (date, genre, artistpic, local, doors, price, starttime, artistweb, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl)
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
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/KennedyUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-kennedy.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
    backupLinks = open(linksBackup, 'w', newline='')
    linkswriter = csv.writer(linksFile)  #Write the file at the end so file is not overwritten if error encountered during scraping
    backupWriter = csv.writer(backupLinks)
    for heresalink in pageanddate:
        linkswriter.writerow((heresalink[0], heresalink[1])) # Write this event to a file so that it will be skipped during future scrapes 
        backupWriter.writerow((heresalink[0], heresalink[1]))
    linksFile.close()
    backupLinks.close()
    print("New used links file created.")
else:
    print("New used links file was NOT created.")
