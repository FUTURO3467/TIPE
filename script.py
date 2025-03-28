import BeatSpectrum as bs
import AudioAnalysis as AudioAnalysis
import datetime
import audio2numpy as a2n

from TIPE.AudioAnalysis import zeroCrossingRate

data, samplerate = a2n.audio_from_file("Sample.mp3")
durationinsec = len(data/samplerate)
if hasattr(data[0], "__len__"):
    data = data[:, 0]

zeroCrossingRate = AudioAnalysis.zeroCrossingRate(data, durationinsec)
print(zeroCrossingRate)

t1 = datetime.datetime.now()
maxs = bs.BeatSpectrum(data, samplerate)
t2 = datetime.datetime.now()
print(t2-t1)
print(maxs)