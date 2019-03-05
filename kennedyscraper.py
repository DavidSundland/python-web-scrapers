#Scrapes Kennedy Center events, but NOT MILLENNIUM STAGE.
# Future - add "Local" variable, adding in NSO, etc., automatically

from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

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
    html = urlopen(url)
    bsObj = BeautifulSoup(html)
    for link in bsObj.findAll("a", href = re.compile("^(\/calendar\/event\/)")):
        newPage = link.attrs["href"] #extract the link
        newPage = newPage.strip("#tickets")  # Some links jump to ticket portion of page - delete this to avoid redundancies
        if newPage not in pages:
            eventurl = "http://www.kennedy-center.org" + newPage
            print(eventurl)
            eventhtml = urlopen(eventurl)
            eventObj = BeautifulSoup(eventhtml)
            year = today.year
            datelong = eventObj.find("h2", {"class":"event-date"}).get_text().strip()
            date = re.findall("[JFMASOND][a-z]+\s+[0-9]{1,2}\,\s+20[12][0-9]", datelong)[0]
            dadate = datetime.datetime.strptime(date.strip(), '%B %d, %Y') #Date is in "March 16, 2017" format.
            if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it (a lot can happen in 2 months):
                break #Kennedy scrapes slowly; events always chronological, so when 2 months passed, can move on to next genre
            time = re.findall("[0-9]{1,2}\:[0-9]{2}\s+[aApP][mM]", datelong) # Extracts the time (should have one or no results)
            if time == []: # if no time results, then must have multiple time and/or date options.  ADD DATE AND TIME MANUALLY AFTER FILE CREATED!!!!
                starttime = eventurl + "#tickets"  #put link to tickets in file to make dates and times easier to manually extract
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
            artist = artist.replace("Washington Performing Arts presents: ", "")
            artist = artist.replace("Washington Performing Arts presents ", "")
            artist = artist.replace("Young Concert Artists Presents ", "")
            artist = artist.replace("KC Jazz Club: ", "")
            artist = artist.replace("The Choral Arts Society of Washington presents:", "Choral Arts Society:")
            artist = artist.replace("Vocal Arts DC presents: ", "")
            artist = artist.replace("Fortas Chamber Music Concerts: ", "")
            artist = artist.replace("The Washington Chorus presents: ", "Washington Chorus: ")
            artist = artist.replace("The Washington Chorus presents ", "Washington Chorus: ")
            if "NSO" in artist or "Washington National Opera" in artist or "Washington Chorus" in artist or "Choral Arts Society" in artist:
                local = "Yes"
            else:
                local = ""
            try:
                pricelong = eventObj.find("div", {"class":"price"}).get_text() #Price range IF not free ("price" class may not exist for free events)
            except:
#                print("Is",eventurl,"free?")  #Perhaps add this back in future - was creating false positives with events that were so far out they were skipped anyway
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
                ticketurl = eventurl + "#tickets"
#                try:
#                    price = re.findall("\$[0-9]{1,4}", datelong)[0]  # If one price
#                except:
#                    price = re.findall("\$[0-9]{1,4}\s+\-\s+\$[0-9]{1,4}", datelong)[0]  # If price range
            description = eventObj.find("div", {"class":"blurbpadding"}).get_text(' ').strip()
            description = description.strip()
            description = re.sub(r'\~+', '~~~', description) # Trim line break when included 
            description = description.replace("\n"," ") # Eliminates annoying carriage returns 
            description = description.replace("\r"," ") # Eliminates annoying carriage returns 
            if (len(description) > 700): # If the description is too long...
                descriptionsentences = description.split(". ") #Let's split it into sentences!
                description = ""
                for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                    description += sentence + ". "
                    if (len(description) > 650):  #Once we exceed 650, dat's da last sentence
                        break
                readmore = eventurl #We had to cut it short, so you can read more at the event page
            else:
                readmore = "" #We included the full description, so no need to have a readmore link
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
            # started attempt to pull dynamically generated info, but it didn't work...
#            tablecells = eventObj.find("td")
#            for onecell in tablecells:
#                try:  # if full-date provided in cell, must be concert date
#                    dateonly = onecell.find("span", {"class":"full-date"}).get_text().strip()
#                    print("found a cell with a date")
#                    date = datetime.datetime.strptime((dateonly.strip() + ', ' + str(year)), '%A, %B %d, %Y').date()
#                    if date < today - datetime.timedelta(days=30):  #If date more than a month in past, event must be in next year
#                        date = datetime.datetime.strptime((dateonly.strip() + ', ' + str(year + 1)), '%A, %B %d, %Y').date()
#                    if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
#                        continue
#                except:
#                    print("found a cell but no date")
            pages.add(newPage)
            pageanddate.add((newPage,datetoday))  # Add link to list, paired with today's date
            try:  # Might crash with weird characters.
                writer.writerow((date, genre, artistpic, local, doors, price, starttime, eventurl, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketurl))
                backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, eventurl, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketurl))
            except:
                UTFcounter += 1
                try:
                    writer.writerow((date, genre, artistpic, local, doors, price, starttime, eventurl, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl))
                    backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, eventurl, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl))
                    print("Using UTF encoding for description", date)
                except:
                    writer.writerow((date, genre, artistpic, local, doors, price, starttime, eventurl, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl))
                    backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, eventurl, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketurl))
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
print("BE SURE TO MAKE SURE THAT TICKET LINKS ARE CORRECT!!!!!  NEW CODE ADDED BUT NOT YET TESTED!!!!!!! ******** ############# !!!!!!!!!!!!!!1 %%%%%%%%%%%55")