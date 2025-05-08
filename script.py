from audioread import NoBackendError

from Utils import AudioAnalysis as AudioAnalysis
from Utils import BeatSpectrum as bs
from Classes import Classes
import audio2numpy as a2n
import json
import os

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
        except a2n.loader.NoBackendError:
            failed+=1
            failedList.append(path)
        print("Analysed and saved  :", files[i].title())

    print(failed,"musics failed to be analyzed", failedList)
