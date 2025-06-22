import time

from audioread import NoBackendError

from Utils import AudioAnalysis as AudioAnalysis
from Utils import BeatSpectrum as bs
from Classes import Classes
import audio2numpy as a2n
import json
import os
import numpy as np
def AnalyseAndSave(f, dest, genre):
    data, samplerate = a2n.audio_from_file(f)
    durationinsec = len(data)/samplerate
    if hasattr(data[0], "__len__"):
        data = data[:, 0]
    SpecFlux = AudioAnalysis.SpectralFlux(data)
    BeaSpe = bs.BeatSpectrum(data, samplerate)
    ZeroXR = AudioAnalysis.zeroCrossingRate(data, durationinsec)
    with open(dest,'r+') as file:
        fdata = json.load(file)
        music = Classes.Music(f,genre, BeaSpe, SpecFlux, ZeroXR)
        fdata["Musics"].append(music.toJSONAble())
        file.seek(0)
        json.dump(fdata, file, indent = 4)
    return music

saveFile = "MusicAnalysisResults.json"
saveTestFile = "MusicTest.json"

def startAnalysis():
    global saveFile
    SourceDirectory = input("Where are the musics ? ")
    howmany = int(input("How many musics do you want to analyze?"))
    whereToBegin = int(input("Begin on which music ?"))
    MusicalGenre = input("Which genre of music is it ?")

    files = os.listdir(SourceDirectory)
    failed = 0
    failedList = []
    for i in range(whereToBegin, min(len(files), whereToBegin+howmany)):
        path = (SourceDirectory+"\\"+files[i])
        print(path)
        print(i-whereToBegin,"/", min(len(files), howmany))
        try:
            AnalyseAndSave(path, saveFile, MusicalGenre)
        except (a2n.loader.NoBackendError,ZeroDivisionError) as e:
            failed+=1
            failedList.append(path)
        print("Analysed and saved  :", files[i].title())

    print(failed,"musics failed to be analyzed", failedList)



def startTest():
    SourceDirectory = input("Where are the musics ? ")
    howmany = int(input("How many musics do you want to test?"))
    whereToBegin = int(input("Begin on which music ?"))
    MusicalGenre = input("Which genre of music is it ?")
    musicsbdd = []
    with open(saveFile, 'r+') as file:
        fdata = json.load(file)
        for elem in fdata["Musics"]:
            musicsbdd.append(Classes.MusicfromJSON(elem))
    files = os.listdir(SourceDirectory)
    failed = 0
    failedList = []
    for i in range(whereToBegin, min(len(files), whereToBegin + howmany)):
        path = (SourceDirectory + "\\" + files[i])
        print(path)
        print(i - whereToBegin, "/", min(len(files), howmany))
        try:
            data, samplerate = a2n.audio_from_file(path)
            durationinsec = len(data) / samplerate
            if hasattr(data[0], "__len__"):
                data = data[:, 0]
            SpecFlux = AudioAnalysis.SpectralFlux(data)
            BeaSpe = bs.BeatSpectrum(data, samplerate)
            ZeroXR = AudioAnalysis.zeroCrossingRate(data, durationinsec)
            music = Classes.Music(path, "", BeaSpe, SpecFlux, ZeroXR)
            distances = []
            for m in musicsbdd:
                distances.append([music.dist(m),m])
            distances.sort(key=lambda x: x[0])
            kclosest=20
            result = [distances[i] for  i in range(kclosest)]
            resultdict = {}
            i=0
            file = open(saveTestFile, 'r')
            fdata = json.load(file)
            for r in result:
                i+=1
                if resultdict.__contains__(r[1].genre):
                    resultdict[r[1].genre] += (1/kclosest)
                else:
                    resultdict.setdefault(r[1].genre, (1/kclosest))
                if i == 5:
                    calculatedgenre = max(resultdict, key=resultdict.get)
                    print("5:",calculatedgenre)
                    success = (calculatedgenre == MusicalGenre)
                    fdata["Count5" + MusicalGenre] += 1
                    newcount = fdata["Count5" + MusicalGenre]
                    fdata["CountSuccess5" + MusicalGenre] += success
                    fdata["SuccessRate5" + MusicalGenre] = round(((fdata["CountSuccess5" + MusicalGenre]) / newcount),
                                                                  4)
                elif i == 10:
                    calculatedgenre = max(resultdict, key=resultdict.get)
                    print("10:", calculatedgenre)
                    success = (calculatedgenre == MusicalGenre)
                    fdata["Count10" + MusicalGenre] += 1
                    newcount = fdata["Count10" + MusicalGenre]
                    fdata["CountSuccess10" + MusicalGenre] += success
                    fdata["SuccessRate10" + MusicalGenre] = round(((fdata["CountSuccess10" + MusicalGenre]) / newcount),
                                                                  4)


            calculatedgenre = max(resultdict, key=resultdict.get)
            print("20:",calculatedgenre)
            success = (calculatedgenre == MusicalGenre)
            print(success)
            fdata["Count20"+MusicalGenre] += 1
            newcount = fdata["Count20"+MusicalGenre]
            fdata["CountSuccess20"+MusicalGenre] += success
            fdata["SuccessRate20"+MusicalGenre] = round(((fdata["CountSuccess20"+MusicalGenre])/newcount), 4)
            file.close()
            file = open(saveTestFile, 'w+')
            json.dump(fdata, file, indent=1)
            file.close()



        except (a2n.loader.NoBackendError, ZeroDivisionError) as e:
            failed += 1
            failedList.append(path)
        print("Tested and Saved  :", files[i].title())

    print(failed, "musics failed to be tested", failedList)

#startAnalysis()
#startTest()

with open(saveFile, 'r+') as file:
    fdata = json.load(file)
    i=0
    print(len(fdata["Musics"]))
    for elem in fdata["Musics"]:
        print(i)
        i+=1
        music = Classes.MusicfromJSON(elem)
        if music.spectral_centroid > 0 : continue
        try:
            data, samplerate = a2n.audio_from_file(music.path)
            if hasattr(data[0], "__len__"):
                data = data[:, 0]
            elem.setdefault("spectral_centroid", AudioAnalysis.spectral_centroid(data, samplerate))
            print("Analysed and saved  :", music.path)
        except (a2n.loader.NoBackendError,ZeroDivisionError) as e:
            print("File open fail")
        file.seek(0)
        json.dump(fdata, file, indent=4)



