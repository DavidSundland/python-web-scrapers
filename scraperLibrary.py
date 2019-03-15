# from urllib.request import urlopen #for pulling info from websites

# import requests  # due to changes in site's encoding, needed to add this import

# from bs4 import BeautifulSoup #for manipulating info pulled from websites
# import re #real expressions
# import csv #comma-separated values
# import datetime


# description: string
# deleteItems: array of items to delete from description (may be unique to each venue)
# numChars: maximum length of description

def descriptionTrim(description, deleteItems, numChars, artistWeb, newHtml):
    description = description.replace("\n"," ").replace("\r"," ").strip() # Eliminates annoying carriage returns & trailing spaces
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
    
