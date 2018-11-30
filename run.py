import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# get current time
timeNow = datetime.today()


# data entry class
# time: time song was played
# songName: name of song
# artist: artist
class entry:
    # constructor
    def __init__(self, timeP, songNameP, artistP, titleP):
        self.time = timeP
        self.songName = songNameP
        self.artist = artistP
        self.title = titleP

    # str output
    def __str__(self):
        x = self.time.split('.')
        songTime = timeNow
        songTime = songTime.replace(hour=int(x[0]), minute=int(x[1]))
        return songTime.strftime('%y.%m.%d_%H:%M') + ";" + self.songName + ";" + self.artist + ";" + self.title

    time = ''
    songName = ''
    artist = ''
    title = ''


# read url to read from
with open("nextHour.txt", "r") as f:
    url = f.readline()

# header for request
headerString = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
Chrome / 41.0 .2272 .101 Safari / 537.36 '

# new session for request
session = requests.Session()

headers = {'User-Agent': headerString}

# perform get request
contents = session.get(url, headers=headers)

# write warning in error case
if contents.status_code != 200:
    errorMessage = 'No correct start URL was supplied, please create a file named\
        "nextHour.txt" in the same folder as the executable and place a working URL in it!'
    print(errorMessage)

# read encoding of contents
encoding = contents.encoding if 'charset' in contents.headers.get(
    'content-type', '').lower() else None

# create BeatifulSoup Html reader instance with correct encoding
soup = BeautifulSoup(
    contents.content, from_encoding=encoding, features="html.parser")

# find title of program
programTitle = soup.find("h2", "musicProgHead").text.strip()

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
    obj = entry(relevantLines[0], relevantLines[1],
                relevantLines[2], programTitle)
    songEntrys.append(obj)

# make a new file every month
resultFileName = 'SWR1_History_' + \
    str(timeNow.year) + '_' + str(timeNow.month) + '.txt'

# print result to file
with open(resultFileName, 'a') as file:
    for obj in songEntrys:
        file.write(str(obj) + '\n')

# find next link

# if new day has started a new request has to be made
if timeNow.hour == 0:
    # find day table
    allDays = soup.find("table", "progDays").find_all("a")

    # find current day of month
    dayToFind = str(timeNow.day)

    # look for current day
    for day in allDays:
        if dayToFind in day.text:
            url = day['href']

    # perform get request for new day
    contents = session.get(url, headers=headers)

    # read encoding of contents
    encoding = contents.encoding if 'charset' in contents.headers.get(
        'content-type', '').lower() else None

    # cook up some new stew
    soup = BeautifulSoup(
        contents.content, from_encoding=encoding, features="html.parser")

# time period for next run
hourToFind = str(timeNow.hour) + ' - ' + \
    str((timeNow + timedelta(hours=1)).hour)

# find all time periods
songTimes = soup.find("div", "progTime pulldown").find_all("a")

# look for correct time period
for songTime in songTimes:
    if hourToFind in songTime.text:
        # write time period to file
        with open('nextHour.txt', 'w') as f:
            print(songTime['href'], file=f)
