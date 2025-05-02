from json import JSONDecodeError

from Utils import AudioAnalysis as AudioAnalysis
from Utils import BeatSpectrum as bs
from Classes import Classes
import audio2numpy as a2n
import json
import io

ch = io.open("MusicAnalysisResults.json", "a")
def AnalyseAndSave(f, dest, genre):
    global ch
    data, samplerate = a2n.audio_from_file(f)

    durationinsec = len(data)/samplerate
    if hasattr(data[0], "__len__"):
        data = data[:, 0]
    SpecFlux = AudioAnalysis.SpectralFlux(data)
    BeaSpe = bs.BeatSpectrum(data, samplerate)
    ZeroXR = AudioAnalysis.zeroCrossingRate(data, durationinsec)
    all = []
    fh = open(dest, 'rb')
    ba = bytearray(fh.read())
    try:
        all = json.loads(ba)
    except JSONDecodeError:
        all = []
    print(f,genre,BeaSpe,SpecFlux.pics,ZeroXR)
    music = Classes.Music(f,genre, BeaSpe, SpecFlux, ZeroXR)
    all.append(music.toJSONAble())
    ch.write(json.dumps(all))
    return music

m1 = AnalyseAndSave("AudioFiles/Sample.mp3", "MusicAnalysisResults.json", "JEUSAIPA")
m2 = AnalyseAndSave("AudioFiles/Megatone - Black and White 03.mp3", "MusicAnalysisResults.json", "JEUSAIPA")
m3 = AnalyseAndSave("AudioFiles/Anonymous Choir - Cantate Domino.mp3","MusicAnalysisResults.json", "JSPNONPLUS")

print(m1.dist(m2), m1.dist(m3))
print(m2.dist(m1), m2.dist(m3))
print(m3.dist(m1), m3.dist(m2))