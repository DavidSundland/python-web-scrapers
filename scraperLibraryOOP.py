import csv #comma-separated values
import re
import datetime

class Scraped: # move to scraperLibraryOOP when scraper completed and tested
    def __init__(self, date, genre, artistpic, local, doors, price, starttime, newhtml, artist, venuelink, venuename, addressurl, venueaddress, description, readmore, musicurl, ticketweb, artisturl):
        self.date = date
        self.genre = genre
        self.artistpic = artistpic
        self.local = local
        self.doors = doors
        self.price = price
        self.starttime = starttime
        self.newhtml = newhtml
        self.artist = artist
        self.venuelink = venuelink
        self.venuename = venuename
        self.addressurl = addressurl
        self.venueaddress = venueaddress
        self.description = description
        self.readmore = readmore
        self.musicurl = musicurl
        self.ticketweb = ticketweb
        self.artisturl = artisturl

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
        
#    def keys(self):
#        return('self', 'date', 'genre', 'artistpic', 'local', 'doors', 'price', 'starttime', 'newhtml', 'artist', 'venuelink', 'venuename', 'addressurl', 'venueaddress', 'description', 'readmore', 'musicurl', 'ticketweb', 'artisturl')
    
#    def _getitem__(self,key):
#        return key
        


### previousScrape - creates list of scraped URLs from list saved during previous scrape
## EXPECTED INPUTS:
# usedLinksFile - name of file to which previously scraped events were noted
# dateFormat - format of date which venue uses
# numDays - minimum date for which previous scrapes NOT be retained
# linkCheckUrl - URL to which event links should be appended to ensure that previously scraped future events did not become invalid.  "" should be provided if event links do not need to be prepended; True should be provided if verification can be skipped
## RETURNS:
# today - today's date as a datetime object
# pages - previously used links; will be supplemented with links checked in current scrape
# pageanddate - links, event date, and scrape date for previously scraped events (will be supplemented w/ current scrapes and become next used links file)
def previousScrape(usedLinksFile, dateFormat, numDays, linkCheckUrl):
    pages = set() #create an empty set of pages
    pageanddate = set() #For list of used links WITH event date and date on which info was added to file
    today = datetime.date.today()
    yesno = ("y","yes","no","n")
    answer = ""
    
    while answer.lower() not in yesno:
        answer = input("Do you want to open used links file? (Skip previously-used links?) ")
    if answer.lower() == "y" or answer.lower() == "yes":
        with open(usedLinksFile, 'r') as previousscrape: 
            reader = csv.reader(previousscrape)
            previousinfo = list(reader)
        for line in previousinfo:
            dadate = datetime.datetime.strptime((line[1].strip()), dateFormat)
            if dadate.date() > today-datetime.timedelta(days=numDays):  #If used link is NOT too old, add it to list
                pageanddate.add((line[0],line[1],line[2]))  #Create list of links that have been checked before
                pages.add(line[0])
                if not linkCheckUrl and dadate.date() > today-datetime.timedelta():
                    if linkCheckUrl.endswith('\\') or line[0].startswith('\\') or linkCheckUrl == '':
                        testurl = linkCheckUrl + line[0]
                    else:
                        testurl = linkCheckUrl + '\\' + line[0]
                    try: #test to ensure that previously-scraped events are still valid...
                        diditwork = requests.get(testurl)
                        if diditwork.status_code > 299:
                            print("Trying to open", testurl, "event on", line[1], "returned an error code")
                    except:
                        print("Trying to open", testurl, "event on", line[1], "did not work.")
        previousscrape.close()
    return [today, pages, pageanddate]

    
### startCSVs - creates CSV files to which scraped information will be saved and creates headers
## EXPECTED INPUTS:
# today - today's date as a datetime object (created by previousScrape)
# fileName - name & path of principal CSV file
# backupFileName - name & path of backup file, BUT WITHOUT .csv EXTENSION
## RETURNS:
# writer & backupwriter - objects via which CSV files will be populated
# datetoday - today's date in string format
def startCsvs(today,fileName,backupFileName):
    write0 = ("DATE", "GENRE", "FEATURE?", "LOCAL?", "DOORS?", "PRICE", "TIME", "ARTIST WEBSITE", "ARTIST", "VENUE LINK", "VENUE NAME", "ADDRESS URL", "VENUE ADDRESS", "DESCRIPTION", "READ MORE URL", "MUSIC URL", "TICKET URL")
    csvFile = open(fileName, 'w', newline='') #The CSV file to which the scraped info will be copied.
    writer = csv.writer(csvFile)
    writer.writerow(write0)
    datetoday = str(datetime.date.today())
    backupfile = backupFileName + datetoday + ".csv"
    backupCSV = open(backupfile, 'w', newline = '') # A back-up file, just in case
    backupwriter = csv.writer(backupCSV)
    backupwriter.writerow(write0)
    return [writer, backupwriter, datetoday, csvFile, backupCSV]

    
### descriptionTrim - EXPECTED INPUTS:
# description: string
# deleteItems: array of items to delete from description (may be unique to each venue)
# numChars: maximum length of description
### RETURNS:
# description - shortened and/or with certain strings removed, if applicable
# readmore - additional info link
def descriptionTrim(object, deleteItems, numChars):
    object.description = object.description.replace("\n"," ").replace("\r"," ").strip() # Eliminates annoying carriage returns & trailing spaces
    object.description = re.sub('\s{2,}',' ',object.description)
    object.description = object.description.replace(u'\xa0', u' ')
    for item in deleteItems:
        object.description = object.description.replace(item,"")
    splitChars = ["#$",". ","! ","? ",".' ",'." '] # sentence ends not always defined by a period; use of a lot of exclamation points or quotations can cause extra-long description...
    pointer = 1
    while len(object.description) > numChars and pointer <= 5: # If the description is too long...
        object.description = descriptionSplit(object.description, splitChars[pointer-1], splitChars[pointer], numChars)
        pointer += 1
    object.readmore = object.artisturl
    if pointer > 1 and object.readmore == "":  
        object.readmore = object.newhtml #Description shortened and no artist web found; offer link to event for more info

def descriptionSplit(description, stripChar, splitChar, numChars):
    descriptionsentences = description.split(splitChar) #Let's split it into sentences!
    description = ""
    for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
        description += sentence + splitChar
        if (len(description) > numChars-100):  #Once we get close to max, dat's da last sentence
            break
    checkChars = stripChar.strip() + splitChar.strip()
    if description.strip().endswith(checkChars):
        description = description.strip().strip(checkChars) + splitChar
    return description.strip()

def killCapAbuse(description):
    if description[-1] == "'" or description[-1] == '"':
        lastPunc = description[-2:]
    else:
        lastPunc = description[-1]
    sentenceEnds = [". ",".' ","! ","? ",'." ']
    description = description.lower()
    for end in sentenceEnds:
        separateSentences = description.split(end)
        description = ""
        for oneSentence in separateSentences:  #Let's rebuild, sentence-by-sentence!
            #Capitalize ONLY the first letter of each sentence - if proper names aren't capitalized or acronyms become faulty, then that's their fault for screaming with ALL CAPS
            oneSentence = oneSentence.lstrip()
            oneSentence = oneSentence[0].upper() + oneSentence[1:]
            if oneSentence.startswith('"'):
                oneSentence = '"' + oneSentence[1].upper() + oneSentence[2:]
            if oneSentence.startswith("'"):
                oneSentence = "'" + oneSentence[1].upper() + oneSentence[2:]
            description += oneSentence + end
        description = description.strip(end)
    description = description.replace(" dc"," DC").replace("washington","Washington") #OK, we'll at least fix the hometown place name, but nothing else
    return description + lastPunc

# function used by getLocalList AND when checking against results
def compactWord(string):
    return re.sub('[\s\-\_\/\.\,]','',string).lower()

# NOTE - as list of local artists gets longer, will want to alphabetize list to allow for more efficient searches
def getLocalList():
    handle = open('local_musicians.txt','r') # opens running list of local musicians
    text = handle.read()
    localList = compactWord(text).split(';')
    handle.close()
    return localList


def titleCase(string):
    words = string.strip().split() 
    returnString = ""
    firstWord = True
    for word in words:
        if not firstWord and word.lower() in ("the", "a", "an", "of", "and", "but", "or", "for", "nor", "to", "on", "at", "from"):
            returnString += word.lower() + " "
            firstWord = False
        else:
            returnString += word.capitalize() + " "
            firstWord = False
    returnString = returnString.replace("Dc","DC")
    returnString = returnString.replace("\(dc","\(DC")
    return returnString.strip()

def saveLinks(datetoday,fileName,backupFileName,pageanddate):
    yesno = ("yes","y","no","n")
    answer = ""
    while answer.lower() not in yesno:
        answer = input("Do you want to write to used links file? (Overwrite existing used links file?) ")
    if answer.lower() == "y" or answer == "yes":
        linksFile = open(fileName, 'w', newline='') #Save the list of links to avoid redundancy in future scraping
        linksBackup = backupFileName + datetoday + ".csv"
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
