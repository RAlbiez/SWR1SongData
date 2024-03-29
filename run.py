#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import json
from types import SimpleNamespace as Namespace
import urllib
import time


# read settings into dictionary
settings = {}
with open(os.path.join(os.getcwd(), "Settings.txt"), 'r') as file:
    sett = file.readlines()

for setting in sett:
    line = setting.split('=',1)
    settings[line[0]] = line[1].replace('\n', '')

# link for lastFM song API
APILink = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&autocorrect=1&api_key=' + \
    settings['API key']

songMetadata = {}

# data entry class
# time: time song was played
# songName: name of song
# artist: artist


class entry:
    # constructor
    def __init__(self, songNameP, artistP, dateP):
        self.songName = songNameP
        self.artist = artistP
        self.date = dateP

    # str output
    def __str__(self):
        # build url for API call
        dicKey = (self.artist,self.songName)
        jsonContent = ''
        if dicKey in songMetadata:
            jsonContent = songMetadata[dicKey]
        else:
            artistAPI = self.artist
            trackAPI = self.songName
            specificLink = APILink + \
                '&artist=' + \
                urllib.parse.quote_plus(
                    artistAPI) + '&track=' + urllib.parse.quote_plus(trackAPI) + '&format=json'

            content = session.get(specificLink, headers=headers)

            # load information from content
            try:
                jsonContent = json.loads(content.text, object_hook=lambda d: Namespace(**d))
            except:
                jsonContent = ''

            songMetadata[dicKey] = jsonContent
        
        albumName = ''
        length = ''
        tags = []
        if hasattr(jsonContent, 'track'):
            if hasattr(jsonContent.track, 'album') and hasattr(jsonContent.track.album, 'title'):
                albumName = jsonContent.track.album.title
            if hasattr(jsonContent.track, 'duration'):
                length = str(int(jsonContent.track.duration) // 1000)
            if hasattr(jsonContent.track, 'toptags') and hasattr(jsonContent.track.toptags, 'tag'):
                for tag in jsonContent.track.toptags.tag:
                    tags.append(tag.name)

        # build output
        outputArgs = [self.date.strftime('%y_%m_%d_%H:%M'), self.songName, self.artist, albumName, length, "[" + ','.join(tags) + "]"]

        # return result
        return ';'.join(outputArgs)

    time = ''
    songName = ''
    artist = ''
    title = ''
    date = ''

urlDate = datetime.strptime(settings['StartDate'],'%d.%m.%Y:%H')

while urlDate.strftime('%d.%m.%Y:%H') != settings['EndDate']:
    print(urlDate)

    url = settings['StationURL'] + urlDate.strftime('%H') + '%3A00&swx_date=' + urlDate.strftime('%Y-%m-%d')

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
    items = soup.find_all("div", {"class": "list-playlist-item"}, "dd")

    # get the text without html tags contained in these items
    results = [i.text for i in items]

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
        
        date = datetime.strptime(relevantLines[0] + ' ' + relevantLines[1],'%d.%m.%Y %H:%M')

        if date.hour == urlDate.hour:
            # create entry object for line
            if len(relevantLines) > 3:
                songName = relevantLines[3]
            else:
                songName = 'Unknown Song'
            
            if len(relevantLines) > 5:
                 songArtist = relevantLines[5]
            else:
                songArtist = 'Unknown Artist'

            obj = entry(songName, songArtist, date)
            songEntrys.append(obj)

    # make a new file every month
    resultFileName = settings['StationName'] + '_History_' + \
        str(urlDate.year) + '_' + str(urlDate.month) + '.txt'

    # join file path
    resultFilePath = os.path.join(os.path.expanduser(
        '~'), settings['path'], resultFileName)

    # print result to file
    with open(resultFilePath.replace('\n', ''), 'a', encoding='utf-8') as file:
        for obj in songEntrys[::-1]:
            file.write(str(obj) + '\n')
    
    urlDate = urlDate + timedelta(hours=1)
