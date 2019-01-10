#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
import json
from types import SimpleNamespace as Namespace
import urllib


# get current time
timeNow = datetime.today()

# read settings into dictionary
settings = {}
with open(os.path.join(os.getcwd(), "Settings.txt"), 'r') as file:
    sett = file.readlines()

for setting in sett:
    x = setting.split('=')
    settings[x[0]] = x[1]

# link for lastFM song API
APILink = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&autocorrect=1&api_key=' + \
    settings['API key'].replace('\n', '')

# data entry class
# time: time song was played
# songName: name of song
# artist: artist


class entry:
    # constructor
    def __init__(self, timeP, songNameP, artistP, titleP, dateP):
        self.time = timeP
        self.songName = songNameP
        self.artist = artistP
        self.title = titleP
        self.date = dateP

    # str output
    def __str__(self):
        # find time at which the song ran
        x = self.time.split('.')
        songTime = timeNow.replace(month=int(self.date[0:2]), day=int(
            self.date[2:4]), hour=int(x[0]), minute=int(x[1]))

        # build url for API call
        artistAPI = self.artist
        trackAPI = self.songName
        specificLink = APILink + \
            '&artist=' + \
            urllib.parse.quote_plus(
                artistAPI) + '&track=' + urllib.parse.quote_plus(trackAPI) + '&format=json'

        content = session.get(specificLink, headers=headers)

        # load information from content
        x = json.loads(content.text, object_hook=lambda d: Namespace(**d))
        albumName = ''
        length = ''
        tags = []
        if hasattr(x, 'track'):
            if hasattr(x.track, 'album') and hasattr(x.track.album, 'title'):
                albumName = x.track.album.title
            if hasattr(x.track, 'duration'):
                length = str(int(x.track.duration) // 1000)
            if hasattr(x.track, 'toptags') and hasattr(x.track.toptags, 'tag'):
                for tag in x.track.toptags.tag:
                    tags.append(tag.name)

        # build output
        outputArgs = [songTime.strftime('%y.%m.%d_%H:%M'), self.songName, self.artist,
                      self.title, albumName, length, "[" + ','.join(tags) + "]"]

        # return result
        return ';'.join(outputArgs)

    time = ''
    songName = ''
    artist = ''
    title = ''
    date = ''


# read url to read from
with open(os.path.join(os.getcwd(), "failedHours.txt"), "r") as f:
    urls = f.readlines()

# header for request
headerString = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
Chrome / 41.0 .2272 .101 Safari / 537.36 '

# new session for request
session = requests.Session()

headers = {'User-Agent': headerString}

for url in urls:
    # perform get request
    contents = session.get(url, headers=headers)

    # write warning in error case
    if contents.status_code != 200:
        errorMessage = 'No correct start URL was supplied, please create a file named\
            "nextHour.txt" in the same folder as the executable and place a \
            working URL in it!'
        print(errorMessage)

    # read encoding of contents
    encoding = contents.encoding if 'charset' in contents.headers.get(
        'content-type', '').lower() else None

    # create BeatifulSoup Html reader instance with correct encoding
    soup = BeautifulSoup(
        contents.content, from_encoding=encoding, features="html.parser")

    # find date
    for x in url.split("/"):
        if "date" in x:
            date = x.split("=")[1][4:8]

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
                    relevantLines[2], programTitle, date)
        songEntrys.append(obj)

    # make a new file every month
    resultFileName = 'SWR1_History_' + \
        str(timeNow.year) + '_' + str(timeNow.month) + '_Fixes.txt'

    # join file path
    resultFilePath = os.path.join(os.path.expanduser(
        '~'), settings['path'], resultFileName)

    # print result to file
    with open(resultFilePath.replace('\n', ''), 'a') as file:
        for obj in songEntrys:
            file.write(str(obj) + '\n')
