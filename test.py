import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class entry:

    def __init__(self, timeP, songNameP, artistP):
        self.time = timeP
        self.songName = songNameP
        self.artist = artistP

    def __str__(self):
        return self.time+";"+self.songName+";"+self.artist
    time = ''
    songName = ''
    artist = ''


timeSub = datetime.today() - timedelta(hours=1)
time = str(timeSub.year) + str(timeSub.month) + \
    str(timeSub.day) + str(timeSub.hour)
url = 'https://www.swr.de/swr1/bw/musikrecherche/-/id=446260/date=' + \
    time+'/did=13840668/nid=446260/1iptl4o/index.html'
print(url)
s = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
session = requests.Session()

headers = {'User-Agent': s}

contents = session.get(url, headers=headers)

encoding = contents.encoding if 'charset' in contents.headers.get(
    'content-type', '').lower() else None
soup = BeautifulSoup(
    contents.content, from_encoding=encoding, features="html.parser")
liItems = soup.find_all("li", {"class": "musicListItem"})

results = [i.text for i in liItems]
resultsTrimmed = []
for x in results:
    s = x.split('\n')
    a = []
    for y in s:
        t = y.strip()
        if t != '':
            a.append(t)
    obj = entry(a[0], a[1], a[2])
    resultsTrimmed.append(obj)

for obj in resultsTrimmed:
    print(obj)
