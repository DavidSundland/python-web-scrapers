#Scrapes Gypsy Sally's events, using - http://www.gypsysallys.com/calendar/  


from urllib.request import urlopen #for pulling info from websites
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

import scraperLibrary #custom library for venue site scraping


usedLinksFile = '../scraped/usedlinks-vinyl.csv'
dateFormat = '%a, %B %d, %Y'
numDays = 30
linkCheckUrl = 'http://www.gypsysallys.com'

[today, pages, pageanddate] = scraperLibrary.previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl)


UTFcounter = 0 # Counter for number of encoding problems

price = "Free!"
doors = " "
venuelink = "http://www.gypsysallys.com/"
venuename = "Gypsy Sally's"
addressurl = "https://goo.gl/maps/omk3qVuLwWG2"
venueaddress = "3401 Water St. NW, Washington, DC 20007"

fileName = '../scraped/scraped-vinyl.csv'
backupFileName = '../scraped/BackupFiles/VinylLoungeScraped'
[writer, backupwriter,datetoday,csvFile,backupCSV] = scraperLibrary.startCsvs(today,fileName,backupFileName)


html = urlopen("http://www.gypsysallys.com/vinyl-lounge-listing/")
bsObj = BeautifulSoup(html)
for link in bsObj.findAll("a",href=re.compile("^(\/event\/)")): #The link to each unique event page begins with "/event/"
    newPage = link.attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
        newhtml = "http://www.gypsysallys.com" + newPage
        html = urlopen(newhtml)
        print(newhtml)
        bsObj = BeautifulSoup(html)
        genre = "Americana" 
        date = bsObj.find("h2", {"class":"dates"}).get_text() 
        dadate = datetime.datetime.strptime((date.strip()), '%a, %B %d, %Y') #Date in table is in day month day, year format.
        if dadate.date() > today+datetime.timedelta(days=61):  #If event is more than 2 months away, skip it for now (a lot can happen in 2 months):
            continue
        time = bsObj.find("span", {"class":"dtstart"}).get_text() # Pulls time AND "Show:" (NOTE - also has class name of "start")
        starttime = re.findall("[0-9]{1,2}:[0-9]{2}\s*[aApP][mM]", time)[0]
        artist = bsObj.find("h1", {"class":"headliners summary"}).get_text() # Event / top artist name
        artist = artist.replace("VINYL LOUNGE OPEN MIC", "Vinyl Lounge Open Mic") 
        artist = artist.replace(", VINYL LOUNGE", "") # Eliminate 'bonus' info about artist being @ Vinyl
        if "closed" in artist.lower() or "private event" in artist.lower():
            continue
        
        localList = scraperLibrary.getLocalList()
        if scraperLibrary.compactWord(artist) in localList:
            local = "Yes"
        else:
            local = ""
        
        if "Open Mic" in artist or "Gordon Sterling" in artist:
            genre = "Potpourri"
            local = "Yes"
        try:
            artistweb = bsObj.find("li", {"class":"web"}).find("a").attrs["href"] 
        except:
            artistweb = ""
        try: # There isn't always a description...
            description = bsObj.find("div", {"class":"bio"}).get_text() 
        except:
            description = ""

        [description, readmore] = scraperLibrary.descriptionTrim(description, [], 800, artistweb, newhtml) #U Street gets shorter descriptions

        descriptionjammed = description.replace(" ","") # Create a string with no spaces
        descriptionJammed = description.replace(" ","") # Create a string with no spaces
        if len(re.findall("[A-Z]{15,}", descriptionJammed)) > 0:
            description = scraperLibrary.killCapAbuse(description)

        musicurl = ""
        try:
            iframes = bsObj.findAll("iframe") # If there's a video, grab it and toss it into the "buy music" column.  BUT - skip iframes that don't contain youtubes
            for onei in iframes:  
                if "youtube" in onei.attrs["src"]:
                    musicurl = onei.attrs["src"]
                    break  # Once first video is found, move along (don't take back-up band's video over headliner; don't have 'else' overwrite found link)
                else:
                    musicurl = ""  # In case there are iframes, but no videos
        except:
            fakevariable = "kibbles"
        ticketweb = ""
        
        artistpic = ""
        pics = bsObj.findAll("img")
        for pic in pics:
            if ".jpg" in pic.attrs["src"]:
                artistpic = pic.attrs["src"]
                break
        artistpic = re.sub('\?w\=[0-9]+\&h\=[0-9]+','',artistpic)
        
        # some artists repeat, but Gypsy doesn't bother providing bios
        if "hergenreder" in artist.lower():
            description = "Hi, I am a song writer in the band Color School. Freinds are urging me to continue playing acoustic, which does make sense. I started playing guitar on acoustic when my hot chic platonic girlfriends would teach me Neal Young songs. We would play on top of Sugar Loaf Mountain near Frederick MD, or at beach week. Guitar was always fireside stuff and we would stay up till the sunrise, partying and playing acoustic guitar. Guess I was doing something right as I got to open for peeps like Peter Case, David Bromberg, and The Radiators. As much as I love playing with Color School, I also relish the firesides, sunrises, and my sweet sweet Dom. Oh, Dominique is my acoustic guitar's name. She is much easier on the ears as far as pressure and volume goes."
            genre = "Americana"
            local = "Yes"
            musicurl = "https://www.reverbnation.com/jerryacoustic"

        if artist == "EMOTiO":
            description = "Vegan Space Metal / Bubblebath Jazz / Rock & Roll & Spaghetti & Meatballs  / Gutter Funk.  Kwesi Lee – Guitar/Keys.  Michael Matthes – Bass/Vocals.  Sean Sidley – Drums.  John Woodridge II – Saxophone."
            genre = "Rock & Pop"
            local = "Yes"
            musicurl = "https://emotio.bandcamp.com/"
            
        if "monasterial" in artist.lower():
            description = "Joseph R Monasterial is a vocalist and acoustic guitarist based in the D.C. area.  Singing has always been an undeniable passion that expresses the beauty of his surprisingly soulful, rich and unique voice. He first taught himself how to play an acoustic guitar when he was 16 and shortly after discovered that he could sing.  Now performing locally in the DMV area and other states like New York, South Carolina, and California, many audiences of all ages have taken delight in his amazing vocal ability.  He performs crossover styles and shows a good balance of a pop vocal style in singing an eclectic blend of tunes.  Blessed with his musical talent coupled with his commitment and diligence, he is on his way to reaching his dreams.  Through his music, Joseph has enriched his life and gained so many wonderful friends."
            genre = "Rock & Pop"
            local = "Yes"
            musicurl = "https://www.reverbnation.com/josephrmonasterial"
            
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
        pages.add(newPage)
        pageanddate.add((newPage,date,datetoday))  # Add link to list, paired with event date and today's date
csvFile.close()
backupCSV.close()

fileName = '../scraped/usedlinks-vinyl.csv'
backupFileName = '../scraped/BackupFiles/VinylLoungeUsedLinks'
scraperLibrary.saveLinks(datetoday,fileName,backupFileName,pageanddate)

if (UTFcounter == 0):
    print("No encoding issues to correct!")
else:
    print("Be sure to correct the", UTFcounter, "events with encoding problems.")
