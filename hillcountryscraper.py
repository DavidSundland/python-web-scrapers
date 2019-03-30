#Scrapes Hill Country BBQ's events, using - http://hillcountry.com/dc/music-calendar/  FOR SPREADSHEET, USE Scraping - Sites w Artist and Ticket Links
#DO, FUTURE - figure out system for genre and local, store photo and video links, artist music link?


############################################################################  #ENCOUNTERED ERROR 403: FORBIDDEN...  (LOOK TO SIXTH AND I FOR POSSIBLE SOLUTION)
#######################################################################  MOTHER-FUCKERS SEEM TO HAVE PROTECTIONS IN PLACE - WHEN BS APPLIED, ONLY CONTENT IS "403 FORBIDDEN"


import requests #urllib didn't work with this site for some reason
from urllib.request import urlopen #for pulling info from websites (will not be used if Error 403 encountered)
import requests #for use if urllib doesn't work 
from bs4 import BeautifulSoup #for manipulating info pulled from websites
import re #real expressions
import csv #comma-separated values
import datetime

try:
    html = urlopen("http://hillcountry.com/dc/music-calendar/")
    bsObj = BeautifulSoup(html)
except:
    url = "http://hillcountry.com/dc/music-calendar/"
    bsObj = BeautifulSoup(requests.get(url).text)

    
pages = set() #create an empty set of pages
#counter = 0  #to keep track of progress while program running

csvFile = open('HillCountryScraped.csv', 'w', newline='') #The CSV file to which the scraped info will be copied.  NOTE - need to define the 'newline' as empty to avoid empty rows in spreadsheet
writer = csv.writer(csvFile)
writer.writerow(("DATE", "TIME", "PRICE", "ARTIST WEBSITE", "ARTIST", "DESCRIPTION", "READ MORE URL", "TICKET URL"))

#for testtest in bsObj.findAll("a"):
#    try:
#        print(testtest.get_text())
#    except:
#        print("Found nuttin")
#html = urlopen("http://hillcountry.com/dc/music-calendar/")
#bsObj = BeautifulSoup(html)

for event in bsObj.findAll("div", {"class":"single-event"}): 
    newPage = event.find("a", {"class":"event-link"}).attrs["href"] #extract the links
    if newPage not in pages: #A new link has been found
#        counter += 1
        print("found a link:",newPage)
        pages.add(newPage)
        newhtml = newPage
        try:
            html = urlopen(newhtml)
            bsObj = BeautifulSoup(html)
        except:
            bsObj = BeautifulSoup(requests.get(newhtml).text)
        artist = bsObj.find("div", {"class":"headliners-name"}).get_text() # Event name
        if "SOLD OUT" in artist.upper():
           continue
        try:
            ticketweb = bsObj.find("a", {"class":"ticket-button"}).attrs["href"] # Get the ticket sales URL; in a try/except in case tickets only at door or free
#            ticketURL = urlopen(ticketweb)
#            tickethtml = urlopen(ticketURL)
#            ticketObj = BeautifulSoup(tickethtml)
#            price = ticketObj.find("div", {"id":"price-range"}).get_text()
#            price = price.strip() # Get rid of beginning and ending carriage returns
        except:
            ticketweb = ""
        price = event.find("span", {"class":"event-time"}).get_text()
        print(newhtml,artist,ticketweb,price)
#        print(artist, price)
#        price = bsObj.find("div", {"class":"info_right"}).get_text() # Pulls the price, which could be a price range, plus bonus text.  MIGHT BE SOLD OUT
#        if "FREE" in price or "Free" in price or "free" in price:
#            price = "FREE!"
#        prices = re.findall("[0-9]{1,3}", price)
#        try:
#            if (prices[0] == prices[1]):
#                price = "$" + prices[0]
#            else:
#                price = price.strip() # Get rid of beginning and ending carriage returns
#                price = price.replace("|","- ")
#                price = price.replace("\n","| ") # Eliminates annoying middle carriage return
#                price = price.replace("\r","| ") # Eliminates annoying middle carriage return
#        except:
#            fakevariable = 3 # damn try won't work without an except, even though I need no except
#        datelong = bsObj.find("div", {"class":"artist_date-single"}).get_text() # This includes the day of the week and (usually? always?) additional text re: age restrictions
#        date = re.findall("[A-Za-z]{3}\s+[A-Za-z]{3}\s+[0-9]{1,2}", datelong)[0]
#        starttime = bsObj.find("div", {"class":"date_right"}).get_text() # Pulls time, including pm (spreadsheet doesn't care about that)
#        description = artist # Start description with artist name
#        if (description[-1] != "!" and description[-1] != "." and description[-1] != ";" and description[-1] != "?"):
#            description += ". "  #Add a period to the end of the artist name if it doesn't alreeady end with punctuation
#        else:
#            description += " "
#        try:
#            openers = bsObj.find("div", {"class":"openers"}).get_text().rstrip(".")
#            openers = re.sub(r'\s{2,}', '', openers)
#            if (re.sub(r'\s+', '', openers) != ""):
#                description += "With: " + openers.replace("|", ", ") + ". "
#        except:
#            description = description
#        for eachartist in bsObj.findAll("div", {"class":"bio"}):  #NOTE - pulls descriptions for all artists (in case 1st artist has no description)
#            try: # There isn't always a description...
#                description += eachartist.get_text() + " " # Get the description, which does include a lot of breaks - will it be a mess?
#            except:
#                description = description
#        try: # There isn't always a description...
#            description += bsObj.find("div", {"class":"artist_content"}).get_text() # Get the description.  Sadly, have not yet figured out how to get rid of annoying "TICKETS ON-SALE..." crap
#        except:
#            description = description
#        description = description.replace("\n"," ") # Eliminates annoying carriage returns 
#        description = description.replace("\r"," ") # Eliminates annoying carriage returns 
#        if (len(description) > 900): # If the description is too long...  
#            descriptionsentences = description.split(".") #Let's split it into sentences!
#            description = ""
#            for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
#                description += sentence + "."
#                if (len(description) > 800):  #Once we exceed 800, dat's da last sentence
#                    break
#            readmore = newhtml #We had to cut it short, so you can read more at the event page
#        else:
#            readmore = "" #We included the full description, so no need to have a readmore link
#        try:
#            artistweb = bsObj.find("div", {"class":"music_links"}).find("a").attrs["href"]  #THIS finds the first instance of a div with a class of "music_links", then digs deeper, finding the first instance w/in that div of a child a, and pulls the href.  BUT - since some artists may not have link, using try/except
#        except:
#            artistweb = newhtml
#        try:  # Might crash with weird characters.  If that happens, skip it.
#            writer = csv.writer(csvFile)
#            writer.writerow((date, starttime, price, artistweb, artist, description, readmore, ticketweb))
#            print(counter) #To watch progress...
#        except:
#            print("Skipped ", date, starttime)
#csvFile.close()