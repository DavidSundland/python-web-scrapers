#Scrapes The Hamilton's events, using - http://live.thehamiltondc.com/listing/  

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
    with open('../scraped/hamiltonusedlinks.csv', 'r') as previousscrape:  
        reader = csv.reader(previousscrape)
        previousinfo = list(reader)
    for line in previousinfo:
        try:
            dadate = datetime.datetime.strptime(line[1].strip(), '%Y-%m-%d') #Newer dates in table are 2017-12-16 format.
        except:
            startdate = re.findall("([SMTWF][a-z]+\s[JFMASOND][a-z]{2}\s[0-9]{1,2})", line[1])[0]  # Some dates for late night events listed as range - want only first date in range
            dadate = datetime.datetime.strptime((startdate +' 2017'), '%A %b %d %Y') #Date in table is in d.o.w. (abbrev) month (abbrev) day format. Added year (program corrected B4 end of '17)
        if dadate.date() > today-datetime.timedelta(days=30):  #If used link is NOT for an event that is more than a month old, add it to list
            pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
            pages.add(line[0])
            testhtml = "http://live.thehamiltondc.com" + line[0]
            try:
                diditwork = urlopen(testhtml)
            except:
                print(testhtml,"caused an error...")
#        else:
#            print(dadate.date(),"skipped")
    previousscrape.close()

counter = 0  #to keep track of progress while program running
UTFcounter = 0
screwydate = set()  #create empty set to keep track of date oddities

local = ""  # Add test for local in future
doors = " "
genre = "Rock & Pop"  # Add test for genre in future
venuelink = "http://live.thehamiltondc.com"
venuename = "The Hamilton"
addressurl = "https://goo.gl/maps/y2BBWdT27AG2"
venueaddress = "600 14th St. NW, Washington, DC 20005"
musicurl = ""

csvFile = open('HamiltonScrapes.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))
datetoday = str(datetime.date.today())
backupfile = "BackupFiles/HamiltonScraped" + datetoday + ".csv"
backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
backupwriter = csv.writer(backupCSV)
backupwriter.writerow(("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL"))

html = urlopen("http://live.thehamiltondc.com/listing/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the link
    if "private-event" in newPage:  #skip the private events
        print("Private event skipped")
        continue
    if newPage not in pages: #A new link has been found
#        counter += 1
        newhtml = "http://live.thehamiltondc.com" + newPage
        eventhtml = urlopen(newhtml)
        eventObj = BeautifulSoup(eventhtml)
        date = eventObj.find("h2", {"class":"dates"}).get_text() # This includes the day of the week, the year and, sometimes, extra spaces.  The spreadsheet doesn't care. (Including year good for E.O.Y.)
        year = today.year
        try:
            dadate = datetime.datetime.strptime((date.strip() + ' ' + str(year)), '%A %b %d %Y')
        except:  # Ran into problems where date range was provided - sometimes multi-date package of tickets was being offered, sometimes they give next day as end date of late night shows
            print("*****\n****Ran into date problem for",newhtml,date," - LOFT date range, ticket series, or other issue?****\n****")
            pages.add(newPage)
            pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
            screwydate.add(newhtml)
            continue
        if dadate.date() < today - datetime.timedelta(days=30):  #If adding the year results in a date more than a month in the past, then event must be in the next year 
            dadate = datetime.datetime.strptime((date.strip() + ' ' + str(year + 1)), '%A %b %d %Y')
        date = dadate.date()
        if date > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months!)
            continue
        time = eventObj.find("span", {"class":"dtstart"}).get_text() # Pulls time, including pm (spreadsheet doesn't care about that) AND "Show:" (NOTE - also has class name of "start")
        starttime = re.findall("([0-9]+:[0-9]{2}\s*[ap]m)", time)[0] #This extracts the time, including am/pm
        try:
            price = eventObj.find("h3", {"class":"price-range"}).get_text().strip() # Pulls the price, which could be a price range
        except: # No price range means that it's free (I hope)
            price = "Free!"
        artist = eventObj.find("h1", {"class":"headliners summary"}).get_text() # Event / top artist name
        artist = artist.replace("Free Late Night Music in The Loft with ","") #Get rid of unnecessary text
        artist = artist.replace("Late Night in The Loft with ","")
        artist = artist.replace(" (Early Show)","")
        artist = artist.replace(" (Late Show)","")
        try:
            artistweb = eventObj.find("li", {"class":"web"}).find("a").attrs["href"]  #THIS finds the first instance of a li with a class of "web", then digs deeper, finding the first instance w/in that li of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
        except:
            artistweb = newhtml
        try: # There isn't always a description...
            description = eventObj.find("div", {"class":"bio"}).get_text() # Get the description, which does include a lot of breaks - will it be a mess?
        except:
            description = ""
        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
        if (len(description) > 700): # If the description is too long...  
            descriptionsentences = description.split(". ") #Let's split it into sentences!
            description = ""
            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
                description += sentence + ". "
                if (len(description) > 650):  #Once we exceed 650, dat's da last sentence
                    break
            readmore = artistweb #We had to cut it short, so you can read more at the event page UNLESS we found an artist link (in which case, go to their page)
        elif artistweb != newhtml:  #If description is short and we found an artist link (so artistweb is different than event page)
            readmore = artistweb #Have the readmore link provide more info about the artist
        else:
            readmore = "" #No artist link and short description - no need for readmore
        try:
            additionalinfo = eventObj.find("h2", {"class":"additional-event-info"}).get_text()
            if "THIS SHOW IS IN OUR LOFT BAR" in additionalinfo:
                description += " NOTE: Show is in loft bar of restaurant."
        except:
            notathing = "Let's toss something in to satisfy the need for an 'except' with a 'try.'"
        if "Fast Eddie" in artist and len(description) < 100: #Fast Eddie plays Hamilton a lot but never has a description
            description = "Serving up a menu of award-winning blues, soul, and rock’n’roll, Fast Eddie & The Slowpokes are fresh off their semi-final finish at the 2017 International Blues Challenge. Their mix of originals and covers stretches from West Coast swing to classic Chicago blues and Memphis soul. The band’s music will get you out of your seat and on your feet."
            genre = "Jazz & Blues"
            local = "Yes"
        elif "Michael Scoglio" in artist and len(description) < 100: #Michael Scoglio plays Hamilton a lot but never has a description
            description = "As the son of a Southern Baptist televangelist, I didn't hear my first rock album until the age of 16. I grew up listening to gospel artists and singing in the church. My first rock album forever changed the way I heard and played music. Since then I have worked to become a top notch player, songwriter, and singer.  I spend my time writing new songs and jamming with other musicians, including Dog City Hoedown, Mike's Swing Thing, and The Electric Peacock Dance Band."
            genre = "Rock & Pop"
            local = "Yes"
            readmore = "https://www.mikescoglio.com/home"
        elif "Mercy Creek" in artist and len(description) < 100: 
            description = "Based in Virginia, Mercy Creek performs original music they call aggressive folk rock. Singer/guitarist Cheryl Nystrom and song writing partner/drummer Jim Ball combine elements of modern folk, world beat, rock, and hints of blues and bluegrass to create music that is fresh and unique. From world beat to folk, the musical styles used in Mercy Creek's songs are anchored by Nystrom's beautiful voice and intelligent lyrics.  Mercy Creek has released 7 independent albums and have been a full time performing act since 1998, playing across the country at clubs, festivals, and concerts."
            genre = "Rock & Pop"
            local = "Yes"
            readmore = "http://www.mercycreek.com/"
        else:
            genre = "Rock & Pop"
            local = ""
        try:
            ticketweb = eventObj.find("a", {"class":"tickets"}).attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door
        except:
            ticketweb = ""
        musicurl = ""
        try:
            iframes = eventObj.findAll("iframe") # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
            for onei in iframes:  
                if "youtube" in onei.attrs["src"]:
                    musicurl = onei.attrs["src"]
                    break  # Once first video is found, move along (don't take back-up band's video over headliner; don't have 'else' overwrite found link)
                else:
                    musicurl = ""  # In case there are iframes, but no videos
        except:
            musicurl = ""
        if "in loft bar" not in description:  #Don't bother with pictures for Loft events - they're always generic pics
            try:
                artistpic = eventObj.find("link", {"rel":"image_src"}).attrs["href"]
            except:
                artistpic = ""
        else:
            artistpic = ""
        if "w=200&h=133" in artistpic:  #Get rid of "The Loft" pics
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
                writer.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                backupwriter.writerow((date, genre, artistpic, local, doors, price, starttime, newhtml, artist.encode('UTF-8'), venuelink, venuename, addressurl, venueaddress, description.encode('UTF-8'), readmore, musicurl, ticketweb))
                print("Using UTF encoding for artist and description", date)
        pages.add(newPage)
        pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
        print(newhtml,date)
csvFile.close()
backupCSV.close()

yesno = ("y","Y","n","N")
answer = ""

while answer not in yesno:
    answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
if answer == "y" or answer == "Y":
    linksBackup = "BackupFiles/HamiltonUsedLinks" + datetoday + ".csv"
    linksFile = open('HamiltonUsedLinks.csv', 'w', newline='') #Save the list of links to avoid redundancy in future scraping
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

if len(screwydate) > 0:
    print("There were date issues with these events:",screwydate)