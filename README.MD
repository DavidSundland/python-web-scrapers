# Miscellaneous Web Scrapers
Python apps to scrape key information from the websites of large music venues in Washington, DC.

## Overview

These web scrapers were written in support of the District Concerts website.  The District Concerts site aggregates information from the websites of over 100 Washington, DC, music venues.  The scrapers in this repository pull key information from the websites of major venues and save that info in CSV files.

TWO IMPORTANT NOTES!:
* While a couple dozen scrapers have been created, they're being moved to GitHub one or three at a time whilst cleaning up the local directory structure.
* If you wanna run these programs, go for it, but you'll need to install Beautiful Soup to do so - https://www.crummy.com/software/BeautifulSoup/.


## More Detailed 'Splanation

These scrapers are being "gitted" primarily so that they are backed up in case of emergency.  They may be of interest to the public eye... but... ehh, probably not.

The majority of DC's music venue websites do not lend themselves to scraping - the sites are not written consistently enough to support accurate and sufficient scraping, or events are so infrequent that it's simpler to copy-and-paste info manually than it is to write a program to retrieve info automatically.  But for the major venues, web scrapers save colossal amounts of time.

Each of the scrapers pull the following information:
* Event date
* Start time
* Ticket cost
* Event URL
* Artist or event name
* Event description

Other information which may be scraped (depending on the website):
* URL for event or artist image
* URL for artist website
* URL for music samples (such as, say, a Soundcloud or Bandcamp page, or a YouTube video)
* Link to ticket sales

A couple of venue websites also lend themselves to categorizing events by genre and/or determining whether or not an artist is local.  However, for most venues, I have not yet been able to create reliable checks for this information.

Each scraper also adds the following information, which makes aggregating the information easier:
* Venue name
* Venue URL
* Venue URL
* Venue address
* Link to Google map for venue
* Whether or not start times are typically when the event actually starts or simply when the doors to the venue are opened.

Each scraper opens one file (if requested by user) and saves two pairs of files.  The files it saves are two copies (one primary, one backup) of the information that has been gathered, and two copies of a running list of events that have been checked.  The file that is opened is a copy of the running list of scraped events - this prevents redundancies, as the same event will not be checked twice (unless the dastardly venue changed the event URL).  Overwriting existing files simplifies the process; identical, date-stamped back-up files are also saved in case a file is overwritten in error.  The user is also asked if the old used links file should be opened (NOT opening the used links file is useful when a scraper is used for the first time or if there were inaccuracies in previously-scraped information) and if a used links file should be created (when a new or revised scraper is being tested, it's best not to save the used links file).

Since each venue website is different, the functionality of each scraper also varies.  All of the scrapers limit the length of the description and remove excessive whitespace.  Some scrapers remove extraneous information, skip certain events (private events, non-music events, etc.), and/or otherwise attempt to clean up some of the crap that is prone to showing up on a particular website.

The end results of the scraping can be seen at: http://www.districtconcerts.com/

## Admitted Shortcomings

The scrapers have evolved over time - when I created my first scraper, I was still pretty fuzzy about how web scraping worked, let alone how I could glean all of the information that I wanted.  If I started anew, I would likely have attempted to make the scrapers more modular, building a library of reusable functions.  That having been said, the variation between the sites that I am scraping would likely cause modularizing a lot of the functionality to be quite challenging.  If this was code that was intended to be used by others, yes.  As personal code...  perhaps in the future.

## Technologies and Tools

* Written with Python
* Programs use Beautiful Soup - https://www.crummy.com/software/BeautifulSoup/ - BS installation is required to run the programs.
