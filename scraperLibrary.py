import csv #comma-separated values
import re
import datetime

### previousScrape - EXPECTED INPUTS:
# usedLinksFile - name of file to which previously scraped events were noted
# dateFormat - format of date which venue uses
# numDays - minimum date for which previous scrapes NOT be retained
# linkCheckUrl - URL to which event links should be appended to ensure that previously scraped future events did not become invalid.  "" should be provided if event links do not need to be prepended; False should be provided if previously scraped events do not need to be verified
### RETURNS:
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

    
### descriptionTrim - EXPECTED INPUTS:
# description: string
# deleteItems: array of items to delete from description (may be unique to each venue)
# numChars: maximum length of description
### RETURNS:
# description - shortened and/or with certain strings removed, if applicable
# readmore - additional info link
def descriptionTrim(description, deleteItems, numChars, artistWeb, newHtml):
    description = description.replace("\n"," ").replace("\r"," ").strip() # Eliminates annoying carriage returns & trailing spaces
    description = re.sub('\s{2,}',' ',description)
    for item in deleteItems:
        description = description.replace(item,"")
    splitChars = ["#$",". ","! ","? ",".' ",'." '] # sentence ends not always defined by a period; use of a lot of exclamation points or quotations can cause extra-long description...
    pointer = 1
    while len(description) > numChars and pointer <= 5: # If the description is too long...
        [description, readmore] = descriptionSplit(description, splitChars[pointer-1], splitChars[pointer], numChars, artistWeb)
        pointer += 1
    if pointer > 1 and artistWeb != newHtml:  #If description is short but we found an artist link
        readmore = artistWeb #Have the readmore link provide more info about the artist
    elif pointer > 1:
        readmore = newHtml
    else:
        readmore = "" #No artist link and short description - no need for readmore
    return [description, readmore]

def descriptionSplit(description, stripChar, splitChar, numChars, artistWeb):
    descriptionsentences = description.split(splitChar) #Let's split it into sentences!
    description = ""
    for sentence in descriptionsentences:  #Let's rebuild, sentence-by-sentence!
        description += sentence + splitChar
        if (len(description) > numChars-100):  #Once we get close to max, dat's da last sentence
            break
    readmore = artistWeb #We had to cut it short, so you can read more at the event or artist page
    checkChars = stripChar.strip() + splitChar.strip()
    if description.strip().endswith(checkChars):
        description = description.strip().strip(checkChars) + splitChar
    return [description.strip(), readmore]

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
