#Scrapes City Winery events, using - https://citywinery.com/washingtondc/tickets.html?view=calendar&month=6&year=2018/  FOR SPREADSHEET, USE Scraping - Basic Sites



from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #regular expressions
import csv #comma-separated values
import datetime
from datetime import date # necessary for properly calculating time differences in months
from dateutil.relativedelta import relativedelta # necessary for properly calculating time differences in months

pages = set() #create an empty set of pages
pageanddate = set() #For list of used links WITH event date and date on which info was added to file
today = datetime.date.today()
yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you open used links file? (Avoid scraping previously scraped links?) ")
if answer == "y" or answer == "Y":
    with open('../scraped/usedlinks-winery.csv', 'r') as previousscrape: 
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        dadate = datetime.datetime.strptime(line[1].strip(), '%m/%d/%y') #Dates are in 7/25/18 format.
        if dadate.date() > today-datetime.timedelta(days=31):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
    previousscrape.close()

UTFcounter = 0 # Counter for number of encoding problems (thusfar not needed for Blues Alley)

local = ""  # Add test for local in future?  Start w/ Twins list?
doors = " "
genre = "Jazz & Blues"
venuelink = "https://citywinery.com/washingtondc/"
venuename = "City Winery"
addressurl = "https://goo.gl/maps/jhjUuxZ44sp"
venueaddress = "1350 Okie St NE, Washington, DC 20002"

csvFile = open('../scraped/scraped-winery.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(today)
backupfile = "../scraped/BackupFiles/WineryScraped" + datetoday + ".csv"
backupCVS = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCVS)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

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
#            artist = re.findall("(.+)\s*\-*\s*[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{1,2}",artistlong)[0]
#            artist = artist.strip()
#            artist = artist.strip("-")
#            artist = artist.strip()
            dateonly = re.findall("[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{1,2}",artistlong)[0]
            try:
                readmore = bsObj.find("li", {"class":"website"}).find("a").attrs["href"]
            except:
                try:
                    readmore = bsObj.find("li", {"class":"facebook"}).find("a").attrs["href"]
                except:
                    readmore = ""
            pageanddate.add((newPage,dateonly,datetoday))  # Add link to list, paired with event date and today's date
            longtime = bsObj.find("span", {"class":"event-date"}).get_text().strip()
            try:
                starttime = re.findall("([0-9]{1,2}\:[0-6][0-9]\s*[aApP][mM])\s*[sS][tT][aA][rR][tT]",longtime)[0]
            except:
                print("Could not find start time for event above...")
                starttime = "8:00 PM"
            prices = bsObj.findAll("span", {"class":"price"})
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
#            description = bsObj.find("div", {"class":"value"}).get_text()
            descriptionWad = bsObj.find("div", {"class":"value"})
            descriptionParagraphs = descriptionWad.findAll("p")
            description = ""
            for paragraph in descriptionParagraphs:
                if re.search("^\$[0-9]+",paragraph.get_text()): # get rid of paragraphs that merely provide pricing info
                    continue
                else:
                    description += paragraph.get_text()
            description = description.replace("\n"," ") # Eliminates annoying carriage returns 
            description = description.replace("\r"," ") # Eliminates annoying carriage returns 
            if (len(description) > 700): # If the description is too long...
                descriptionsentences = description.split(". ") #Let's split it into sentences!
                description = ""
                for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                    description += sentence + ". "
                    if (len(description) > 650):  #Once we exceed 650, dat's da last sentence
                        break
            artistpic = bsObj.find("p", {"class":"product-image"}).find("img").attrs["src"]
            ticketweb = newhtml
            try:  # Might crash with weird characters.
                writer.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
                backupwriter.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb))
            except:
                UTFcounter += 1
                try:
                    writer.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    backupwriter.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    print("Using UTF encoding for description", dateonly)
                except:
                    writer.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    backupwriter.writerow((dateonly, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                    print("Using UTF encoding for artist and description", dateonly)
csvFile.close()
backupCVS.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "../scraped/BackupFiles/WineryUsedLinks" + datetoday + ".csv"
    linksFile = open('../scraped/usedlinks-winery.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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
