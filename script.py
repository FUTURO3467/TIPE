import time

from audioread import NoBackendError

from Classes.Classes import MusicfromJSON
from Utils import AudioAnalysis as AudioAnalysis
from Utils import BeatSpectrum as bs
from Classes import Classes
import audio2numpy as a2n
import json
import os
import numpy as np
from math import sqrt

from Utils.AudioAnalysis import spectral_centroid


def AnalyseAndSave(f, dest, genre):
    data, samplerate = a2n.audio_from_file(f)
    durationinsec = len(data)/samplerate
    if hasattr(data[0], "__len__"):
        data = data[:, 0]
    SpecFlux = AudioAnalysis.SpectralFlux(data, samplerate)
    BeaSpe = bs.BeatSpectrum(data, samplerate)
    ZeroXR = AudioAnalysis.zeroCrossingRate(data, durationinsec)
    spec_centro = AudioAnalysis.spectral_centroid(data, samplerate)
    with open(dest,'r+') as file:
        fdata = json.load(file)
        music = Classes.Music(f,genre, BeaSpe, SpecFlux, ZeroXR,spec_centro)
        fdata["Musics"].append(music.toJSONAble())
        file.seek(0)
        json.dump(fdata, file, indent = 4)
        

    return music

saveFile = "MusicAnalysisResults.json"
saveTestFile = "Resultats_Test_Sans_Jazz.json"

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


def registerResult(calculated_genre , musical_genre, fdata, number=20):
    #print(number,":", calculated_genre)
    success = (calculated_genre == musical_genre)
    if ("Count"+str(number) + musical_genre) in fdata:
        fdata["Count"+str(number) + musical_genre] += 1
        newcount = fdata["Count"+str(number) + musical_genre]
        fdata["CountSuccess"+str(number) + musical_genre] += success
        fdata["SuccessRate"+str(number) + musical_genre] = round(((fdata["CountSuccess"+str(number) + musical_genre]) / newcount), 4)
    else:
        fdata["Count"+str(number) + musical_genre] = 1
        fdata["CountSuccess"+str(number) + musical_genre] = success
        fdata["SuccessRate"+str(number) + musical_genre] = round(success, 4)

def startTest(ignore_genre=None):
    SourceDirectory = input("Where are the musics ? ")
    howmany = int(input("How many musics do you want to test?"))
    whereToBegin = int(input("Begin on which music ?"))
    MusicalGenre = input("Which genre of music is it ?")
    musiquebdd = []
    with open(saveFile, 'r+') as file:
        fdata = json.load(file)
        for elem in fdata["Musics"]:
            if elem["genre"] != ignore_genre:
                musiquebdd.append(Classes.MusicfromJSON(elem))
    print("Taille de la BDD :", len(musiquebdd))
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
            SpecFlux = AudioAnalysis.SpectralFlux(data, samplerate)
            BeaSpe = bs.BeatSpectrum(data, samplerate)
            ZeroXR = AudioAnalysis.zeroCrossingRate(data, durationinsec)
            spectral_centroid = AudioAnalysis.spectral_centroid(data, samplerate)
            music = Classes.Music(path, MusicalGenre, BeaSpe, SpecFlux, ZeroXR, spectral_centroid)
            distances = []
            for m in musiquebdd:
                distances.append([music.dist(m),m])
            distances.sort(key=lambda x: x[0])
            kclosest = round(sqrt(len(musiquebdd)))
            result = [distances[i] for  i in range(kclosest)]
            resultdict = {}
            i=0
            file = open(saveTestFile, 'r')
            fdata = json.load(file)
            fdata["Musics"].append(music.toJSONAble())
            for r in result:
                i += 1
                if resultdict.__contains__(r[1].genre):
                    resultdict[r[1].genre] += (1 / kclosest)
                else:
                    resultdict.setdefault(r[1].genre, (1 / kclosest))
                if i == 5:
                    calculated_genre = max(resultdict, key=resultdict.get)
                    registerResult(calculated_genre, music.genre, fdata, 5)
                elif i == 10:
                    calculated_genre = max(resultdict, key=resultdict.get)
                    registerResult(calculated_genre, music.genre, fdata, 10)
                elif i == 20:
                    calculated_genre = max(resultdict, key=resultdict.get)
                    registerResult(calculated_genre, music.genre, fdata, 20)

            calculated_genre = max(resultdict, key=resultdict.get)
            registerResult(calculated_genre, music.genre, fdata, kclosest)

            file.close()
            file = open(saveTestFile, 'w+')
            json.dump(fdata, file, indent=1)
            file.close()



        except (a2n.loader.NoBackendError, ZeroDivisionError) as e:
            failed += 1
            failedList.append(path)
        print("Tested and Saved  :", files[i].title())

    print(failed, "musics failed to be tested", failedList)

def test_precalc(ignore_genre=None):
    musiquebdd = []
    genre_dict = {}
    nb_genres = 0
    with open(saveFile, 'r+') as file:
        fdata = json.load(file)
        for elem in fdata["Musics"]:
            if elem["genre"] != ignore_genre:
                musiquebdd.append(Classes.MusicfromJSON(elem))
                if not elem["genre"] in genre_dict:
                    genre_dict[elem["genre"]] = nb_genres
                    nb_genres+=1
    print("Indices utilisés :", genre_dict)
    print("Taille de la base de données :", len(musiquebdd))
    confusion = [[0 for _ in range(nb_genres)] for _ in range(nb_genres)]
    with open(saveTestFile, 'r+') as file:
        fdata = json.load(file)
        nb_calcul = 0
        for elem in fdata["Musics"]:
            music = MusicfromJSON(elem)
            if music.genre == ignore_genre: continue
            distances = []
            for m in musiquebdd:
                distances.append([music.dist(m),m])
            distances.sort(key=lambda x: x[0])
            k=round(sqrt(len(musiquebdd)))
            dists = [distances[i] for  i in range(k)]
            resultats_dict = {}
            i=0
            for r in dists:
                i+=1
                if resultats_dict.__contains__(r[1].genre):
                    resultats_dict[r[1].genre] += (1/k)
                else:
                    resultats_dict.setdefault(r[1].genre, (1/k))
                if i == 5:
                    calculated_genre = max(resultats_dict, key=resultats_dict.get)
                    registerResult(calculated_genre, music.genre, fdata, 5)
                elif i == 10:
                    calculated_genre = max(resultats_dict, key=resultats_dict.get)
                    registerResult(calculated_genre, music.genre, fdata, 10)
                elif i == 20:
                    calculated_genre = max(resultats_dict, key=resultats_dict.get)
                    registerResult(calculated_genre, music.genre, fdata, 20)

            calculated_genre = max(resultats_dict, key=resultats_dict.get)
            registerResult(calculated_genre, music.genre, fdata, k)
            confusion[genre_dict[calculated_genre]][genre_dict[music.genre]] += 1
            nb_calcul += 1
            if nb_calcul%100 == 0:
                print(f"{nb_calcul} Musiques calculées...")
        fdata["Confusion_"+str(k)] = confusion
        file2 = open(saveTestFile, 'w+')
        json.dump(fdata, file2, indent=1)
        file2.close()
    print(confusion)
    print("Test terminé")
#test_precalc()
#startAnalysis()
#startTest()
def calculate_for_all(key, func, ignore_condition, filepath):
    with open(filepath, 'r+') as file:
        fdata = json.load(file)
        i = 0
        print(len(fdata["Musics"]))
        for elem in fdata["Musics"]:
            print(i)
            i += 1
            music = Classes.MusicfromJSON(elem)
            if ignore_condition(music): continue
            try:
                data, samplerate = a2n.audio_from_file(music.path)
                if hasattr(data[0], "__len__"):
                    data = data[:, 0]
                res = func(data, samplerate)
                elem.setdefault(key, res)
                print(res)
                fdata["Musics"][i-1][key] = res
                print("Analysed and saved  :", music.path)
            except (a2n.loader.NoBackendError, ZeroDivisionError) as e:
                print("File open fail")
            file.seek(0)
            json.dump(fdata, file, indent=4)
#calculate_for_all("beatspectrum", bs.BeatSpectrum, lambda a : len(a.beatspectrum) == 20, saveTestFile)
test_precalc(ignore_genre="Jazz")
#startTest()
