import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# data entry class
# time: time song was played
# songName: name of song
# artist: artist
class entry:
    # constructor
    def __init__(self, timeP, songNameP, artistP):
        self.time = timeP
        self.songName = songNameP
        self.artist = artistP

    # str output
    def __str__(self):
        return self.time + ";" + self.songName + ";" + self.artist

    time = ''
    songName = ''
    artist = ''


# get current time
timeNow = datetime.today() - timedelta(hours=1)
timeStr = str(timeNow.year) + str(timeNow.month) + \
    str(timeNow.day) + str(timeNow.hour)

# put together url
url = 'https://www.swr.de/swr1/bw/musikrecherche/-/id=446260/date=' + \
    timeStr + '/did=13840668/nid=446260/1iptl4o/index.html'

# !!!Warning!!!
print("warning, url broken at this point, manually adjust for testing")

# header for request
headerString = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
 Chrome / 41.0 .2272 .101 Safari / 537.36 '

# new session for request
session = requests.Session()

headers = {'User-Agent': headerString}

# perform get request
contents = session.get(url, headers=headers)

# read encoding of contents
encoding = contents.encoding if 'charset' in contents.headers.get(
    'content-type', '').lower() else None

# create BeatifulSoup Html reader instance with correct encoding
soup = BeautifulSoup(
    contents.content, from_encoding=encoding, features="html.parser")

# find all li tags from class "musicListItem"
liItems = soup.find_all("li", {"class": "musicListItem"})

# get the text without html tags contained in these items
results = [i.text for i in liItems]

# parse the result into  entry objects
songEntrys = []
for unchangedData in results:
    # split line at newline char to find the relevant lines
    dataLines = unchangedData.split('\n')
    relevantLines = []
    for line in dataLines:
        # remove whitespace
        lineStripped = line.strip()
        # add line to result if there is still text in line
        if lineStripped != '':
            relevantLines.append(lineStripped)
    # create entry object for line
    obj = entry(relevantLines[0], relevantLines[1], relevantLines[2])
    songEntrys.append(obj)

# print it to console for debug purposes
for obj in songEntrys:
    print(obj)
