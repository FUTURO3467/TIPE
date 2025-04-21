from json import JSONDecodeError

from TIPE.Utils import AudioAnalysis as AudioAnalysis
from TIPE.Utils import BeatSpectrum as bs
from TIPE.Classes import Classes
import audio2numpy as a2n
import json
import io

ch = io.open("MusicAnalysisResults.json", "w")
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
    try:
        all = json.loads(dest)
    except JSONDecodeError:
        all = []
    print(f,genre,BeaSpe,SpecFlux,ZeroXR)
    music = Classes.Music(f,genre, BeaSpe, SpecFlux, ZeroXR)
    all.append(music.toJSONAble())
    ch.write(json.dumps(all))

AnalyseAndSave("AudioFiles/Anonymous Choir - Cantate Domino.mp3", "MusicAnalysisResults.json", "JEUSAIPA")