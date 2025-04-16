from TIPE.Utils import AudioAnalysis as AudioAnalysis
import datetime
import audio2numpy as a2n

data, samplerate = a2n.audio_from_file("AudioFiles/Anonymous Choir - Cantate Domino.mp3")


durationinsec = len(data)/samplerate
if hasattr(data[0], "__len__"):
    data = data[:, 0]

t1 = datetime.datetime.now()
y = AudioAnalysis.SpectralFlux(data)
print(y)

#maxs = bs.BeatSpectrum(data, samplerate)
t2 = datetime.datetime.now()
print(t2-t1)