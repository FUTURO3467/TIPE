from Classes.Classes import MusicfromJSON
from Utils import AudioAnalysis as AudioAnalysis
from Utils import BeatSpectrum as bs
from Classes import Classes
import audio2numpy as a2n
import json
import os
from math import sqrt

def analyser_et_sauvgarder(f, dest, genre):
    donnees, freq = a2n.audio_from_file(f)
    duree = len(donnees)/freq
    if hasattr(donnees[0], "__len__"):
        donnees = donnees[:, 0]
    SpecFlux = AudioAnalysis.flux_spectral(donnees)
    BeaSpe = bs.BeatSpectrum(donnees, freq)
    ZeroXR = AudioAnalysis.frequence_annulation(donnees, duree)
    spec_centro = AudioAnalysis.centroid_spectral(donnees, freq)
    with open(dest,'r+') as file:
        fdata = json.load(file)
        music = Classes.Music(f,genre, BeaSpe, SpecFlux, ZeroXR,spec_centro)
        fdata["Musics"].append(music.toJSONAble())
        file.seek(0)
        json.dump(fdata, file, indent = 4)
    return music

sauvegarde_entrainement = "MusicAnalysisResults.json"
sauvegarde_test = "Resultats_Test_Sans_Jazz.json"

def Entrainement():
    global sauvegarde_entrainement
    repertoire_source = input("Where are the musics ? ")
    nb_musiques = int(input("How many musics do you want to analyze?"))
    indice_debut = int(input("Begin on which music ?"))
    genre_musical = input("Which genre of music is it ?")
    fichiers = os.listdir(repertoire_source)
    erreurs = 0
    liste_erreurs = []
    for i in range(indice_debut, min(len(fichiers), indice_debut+nb_musiques)):
        path = (repertoire_source+"\\"+fichiers[i])
        print(path)
        print(i-indice_debut,"/", min(len(fichiers), nb_musiques))
        try:
            analyser_et_sauvgarder(path, sauvegarde_entrainement, genre_musical)
        except (a2n.loader.NoBackendError,ZeroDivisionError) as e:
            erreurs+=1
            liste_erreurs.append(path)
        print("Analysed and saved  :", fichiers[i].title())

    print(erreurs,"musics failed to be analyzed", liste_erreurs)
def enregistrerResultats(genre_calculé, genre_musical, fichier_sauvegarde, nb=20):
    reussi = (genre_calculé == genre_musical)
    if ("Count" + str(nb) + genre_musical) in fichier_sauvegarde:
        fichier_sauvegarde["Count" + str(nb) + genre_musical] += 1
        nouv_nb = fichier_sauvegarde["Count" + str(nb) + genre_musical]
        fichier_sauvegarde["CountSuccess" + str(nb) + genre_musical] += reussi
        fichier_sauvegarde["SuccessRate" + str(nb) + genre_musical] = round(
            (fichier_sauvegarde["CountSuccess" + str(nb) + genre_musical])/nouv_nb
            ,4
            )
    else:
        fichier_sauvegarde["Count" + str(nb) + genre_musical] = 1
        fichier_sauvegarde["CountSuccess" + str(nb) + genre_musical] = reussi
        fichier_sauvegarde["SuccessRate"+str(nb)+genre_musical] = round(reussi, 4)

def Test(ignore_genre=None):
    repertoire_source = input("Where are the musics ? ")
    nb_musiques = int(input("How many musics do you want to Test?"))
    indice_debut = int(input("Begin on which music ?"))
    genre_musical = input("Which genre of music is it ?")
    musiquebdd = []
    with open(sauvegarde_entrainement, 'r+') as file:
        fdata = json.load(file)
        for elem in fdata["Musics"]:
            if elem["genre"] != ignore_genre:
                musiquebdd.append(Classes.MusicfromJSON(elem))
    print("Taille de la BDD :", len(musiquebdd))
    files = os.listdir(repertoire_source)
    erreurs = 0
    liste_erreurs = []
    for i in range(indice_debut, min(len(files), indice_debut + nb_musiques)):
        chemin = (repertoire_source + "\\" + files[i])
        print(chemin)
        print(i - indice_debut, "/", min(len(files), nb_musiques))
        try:
            donnees, freq = a2n.audio_from_file(chemin)
            duree = len(donnees) / freq
            if hasattr(donnees[0], "__len__"):
                donnees = donnees[:, 0]
            SpecFlux = AudioAnalysis.flux_spectral(donnees)
            BeaSpe = bs.BeatSpectrum(donnees, freq)
            ZeroXR = AudioAnalysis.frequence_annulation(donnees, duree)
            spectral_centroid = AudioAnalysis.centroid_spectral(donnees, freq)
            musique = Classes.Music(chemin, genre_musical, BeaSpe, SpecFlux, ZeroXR, spectral_centroid)
            distances = []
            for m in musiquebdd:
                distances.append([musique.dist(m),m])
            distances.sort(key=lambda x: x[0])
            kpp = round(sqrt(len(musiquebdd)))
            kpp = kpp + (1-kpp%2)
            resultats = [distances[i] for  i in range(kpp)]
            resultats_dict = {}
            file = open(sauvegarde_test, 'r')
            fdata = json.load(file)
            fdata["Musics"].append(musique.toJSONAble())
            for r in resultats:
                if resultats_dict.__contains__(r[1].genre):
                    resultats_dict[r[1].genre] += (1 / kpp)
                else:
                    resultats_dict.setdefault(r[1].genre, (1 / kpp))

            calculated_genre = max(resultats_dict, key=resultats_dict.get)
            enregistrerResultats(calculated_genre, musique.genre, fdata, kpp)

            file.close()
            file = open(sauvegarde_test, 'w+')
            json.dump(fdata, file, indent=1)
            file.close()
        except (a2n.loader.NoBackendError, ZeroDivisionError) as e:
            erreurs += 1
            liste_erreurs.append(chemin)
        print("Tested and Saved  :", files[i].title())
    print(erreurs, "musics failed to be tested", liste_erreurs)

def calculer_pour_tous(key, func, ignore_condition, filepath):
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
                data, samplerate = a2n.audio_from_file(music.chemin)
                if hasattr(data[0], "__len__"):
                    data = data[:, 0]
                res = func(data, samplerate)
                elem.setdefault(key, res)
                print(res)
                fdata["Musics"][i-1][key] = res
                print("Analysed and saved  :", music.chemin)
            except (a2n.loader.NoBackendError, ZeroDivisionError) as e:
                print("File open fail")
            file.seek(0)
            json.dump(fdata, file, indent=4)

#calculer_pour_tous("beatspectrum", bs.BeatSpectrum, lambda a : len(a.beatspectrum) == 20, saveTestFile)
#Test()
def test_precalc(ignore_genre=None):
    musiquebdd = []
    genre_dict = {}
    nb_genres = 0
    with open(sauvegarde_entrainement, 'r+') as file:
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
    with open(sauvegarde_test, 'r+') as file:
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
                    enregistrerResultats(calculated_genre, music.genre, fdata, 5)
                elif i == 10:
                    calculated_genre = max(resultats_dict, key=resultats_dict.get)
                    enregistrerResultats(calculated_genre, music.genre, fdata, 10)
                elif i == 20:
                    calculated_genre = max(resultats_dict, key=resultats_dict.get)
                    enregistrerResultats(calculated_genre, music.genre, fdata, 20)

            calculated_genre = max(resultats_dict, key=resultats_dict.get)
            enregistrerResultats(calculated_genre, music.genre, fdata, k)
            confusion[genre_dict[calculated_genre]][genre_dict[music.genre]] += 1
            nb_calcul += 1
            if nb_calcul%100 == 0:
                print(f"{nb_calcul} Musiques calculées...")
        fdata["Confusion_"+str(k)] = confusion
        file2 = open(sauvegarde_test, 'w+')
        json.dump(fdata, file2, indent=1)
        file2.close()
    print(confusion)
    print("Test terminé")
test_precalc(ignore_genre="Jazz")
