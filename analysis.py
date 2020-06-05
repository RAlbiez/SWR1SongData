import glob
import os

swr1data = []
swr3data = []
swr4data = []
dasdingdata = []

for x in ['SWR1', 'SWR3', 'SWR4', 'DASDING']:
    filepath = os.path.join(os.path.expanduser('~'), 'SongData', x+'*')
    for filename in glob.glob(filepath):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if x == 'SWR1':
                    swr1data.append(line.replace('\n', '').split(';'))
                elif x == 'SWR3':
                    swr3data.append(line.replace('\n', '').split(';'))
                elif x == 'SWR4':
                    swr4data.append(line.replace('\n', '').split(';'))
                else:
                    dasdingdata.append(line.replace('\n', '').split(';'))

alldata = {'SWR1' : swr1data, 'SWR3' : swr3data, 'SWR4' : swr4data, 'DASDING' : dasdingdata}

for station, data in alldata.items():
    groupedbysong = {}
    for d in data:
        key = (d[1],d[2])
        if key in groupedbysong:
            groupedbysong[key] +=1
        else:
            groupedbysong[key] = 1
    
    groupedbysongsorted = {k: v for k, v in sorted(groupedbysong.items(), key = lambda item: item[1], reverse=True)}

    groupedbysongandday = {}
    for d in data:
        key = (d[1],d[2],d[0].rsplit('_',1)[0])
        if key in groupedbysongandday:
            groupedbysongandday[key] +=1
        else:
            groupedbysongandday[key] = 1
    
    #groupedbysonganddaysorted = {k: v for k, v in sorted(groupedbysongandday.items(), key = lambda item: item[1], reverse=True)}

    print(station+':\n')

    i=0
    for key, value in groupedbysongsorted.items():
        if i == 10:
            break
        i+=1
        print(str(value) +'\t\t'+ key[0] + " : " + key[1])

    totalplayed = len(data)

    diversityscore = sum([1/x for x in groupedbysong.values()]) / len(groupedbysong.values())

    print("\nDiversity Score:\t"+ str(diversityscore))

    #percentage of songs heard more then once if listening the whole day
    replayscore = sum([x-1 for x in groupedbysongandday.values()]) / totalplayed

    print("Replay Score:\t\t"+ str(replayscore))

    songsplayed = len(data)

    print("Songs Played:\t\t"+ str(songsplayed))

    librarysize = len(groupedbysong.values())

    print("Library Size:\t\t"+ str(librarysize))

    singlerunners = len(list(filter(lambda x: x == 1, groupedbysong.values())))

    print("Single Runners:\t\t"+ str(singlerunners))

    datawithsonglength = list(filter(lambda x: x.isdigit() and int(x)>0, [y[4] for y in data]))
    averagesonglength = sum([int(x) for x in datawithsonglength])/len(datawithsonglength)
    songtimeplayed = songsplayed * averagesonglength
    percentagecoveredbymusic = songtimeplayed / (60*60*24*360)

    print("Covered by music:\t"+ str(percentagecoveredbymusic))

    print("\n\n")





