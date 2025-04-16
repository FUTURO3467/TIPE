import BeatSpectrum as bs
import AudioAnalysis as AudioAnalysis
import datetime
import audio2numpy as a2n
import matplotlib.pyplot as plt

data, samplerate = a2n.audio_from_file("Anonymous Choir - Cantate Domino.mp3")


durationinsec = len(data)/samplerate
if hasattr(data[0], "__len__"):
    data = data[:, 0]

t1 = datetime.datetime.now()
y = AudioAnalysis.SpectralFlux(data)

#maxs = bs.BeatSpectrum(data, samplerate)
t2 = datetime.datetime.now()
print(t2-t1)