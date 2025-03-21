from scipy.io import wavfile
import scipy.signal as sig
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import pydub
import audio2numpy as a2n


def read(f, normalized=False):
  """MP3 to numpy array"""
  a = pydub.AudioSegment.from_mp3(f)
  y = np.array(a.get_array_of_samples())
  if a.channels == 2:
    y = y.reshape((-1, 2))
  if normalized:
    return a.frame_rate, np.float32(y) / 2 ** 15
  else:
    return a.frame_rate, y

def mean(a):
  tot = 0
  l = len(a)
  for i in range(l):
    tot += a[i]
  return (tot/l)

def maxwithpos(a):
  m = max(a)
  mi = 0
  for i in range(len(a)):
    if a[i] == m:
      mi = i
  return [m, mi]

def getpos(e,a):
  for i in range(len(a)):
    if a[i] == e:
      return i
  return -1


def AutoCorrelation(envelope,EnvelopeDecimated,MinBPM,MaxBPM):
  end = math.ceil((60 * EnvelopeDecimated) / (MinBPM))

  start = math.ceil((60 * EnvelopeDecimated) / (MaxBPM))

  ts = len(envelope) - end

  xc = np.zeros(end)

  for i in range(start,end):
    sum = 0
    for j in range(1,ts):
      sum += (envelope[j] * envelope[j + i])
    xc[i] += sum
  return xc


def SubBandDWT(Signal,Fs,L,H):
  LowFrequencyBand = L / (Fs / 2);

  [numerator, denominator] = sig.butter(2, LowFrequencyBand, 'high')
  if hasattr(Signal[0], "__len__"):
    Signal = Signal[:,0]
  FiltredSignal = sig.filtfilt(numerator, denominator, Signal)

  HighFrequencyBand = H / (Fs / 2)

  [numerator, denominator] = sig.butter(2, HighFrequencyBand, 'low')

  SubBand = sig.filtfilt(numerator, denominator, FiltredSignal)

  return [SubBand, numerator, denominator]

def Envelope(SubBand,DecimateValue,new_fs,numerator,denominator):

  SubBand = abs(SubBand)
  LowPassSubBand = sig.filtfilt(numerator, denominator, SubBand)

  bands = sig.decimate(LowPassSubBand, DecimateValue)

  MeanRemoval = bands - mean(bands)

  Tw = 0.1
  Nw = Tw * new_fs
  w = np.ones(int(Nw))/Nw

  RectifiedEnvelope = np.convolve(MeanRemoval, w, 'same')
  return RectifiedEnvelope

t1 = time.process_time()
#Paramètres
MinBPM=40
MaxBPM=200

new_fs = 22050
EnvelopeDecimated=200



data, samplerate = a2n.audio_from_file('Megatone - Black and White 03.mp3')

t = np.arange(len(data)) / float(samplerate)

[SubBand1, numerator1, denominator1]=SubBandDWT(data,samplerate,1,200)

[SubBand2, numerator2, denominator2]=SubBandDWT(data,samplerate,200,400)

[SubBand3, numerator3, denominator3]=SubBandDWT(data,samplerate,400,800)

[SubBand4, numerator4, denominator4]=SubBandDWT(data,samplerate,800,1600)

[SubBand5, numerator5, denominator5]=SubBandDWT(data,samplerate,1600,3200)

[SubBand6, numerator6, denominator6]=SubBandDWT(data,samplerate,3200,6400)

DecimateValue = math.ceil(samplerate/new_fs)


Envelope1=Envelope(SubBand1, DecimateValue, new_fs, numerator1, denominator1)

Envelope2=Envelope(SubBand2, DecimateValue, new_fs, numerator2, denominator2)

Envelope3=Envelope(SubBand3, DecimateValue, new_fs, numerator3, denominator3)

Envelope4=Envelope(SubBand4, DecimateValue, new_fs, numerator4, denominator4)

Envelope5=Envelope(SubBand5, DecimateValue, new_fs, numerator5, denominator5)

Envelope6=Envelope(SubBand6, DecimateValue, new_fs, numerator6, denominator6)


c = math.floor((samplerate/DecimateValue)/EnvelopeDecimated)

EnvelopeDecimated1=[Envelope1[i*c] for i in range(int(len(Envelope1)/c))]
EnvelopeDecimated2=[Envelope2[i*c] for i in range(int(len(Envelope2)/c))]
EnvelopeDecimated3=[Envelope3[i*c] for i in range(int(len(Envelope3)/c))]
EnvelopeDecimated4=[Envelope4[i*c] for i in range(int(len(Envelope4)/c))]
EnvelopeDecimated5=[Envelope5[i*c] for i in range(int(len(Envelope5)/c))]
EnvelopeDecimated6=[Envelope6[i*c] for i in range(int(len(Envelope6)/c))]

print(c, len(EnvelopeDecimated1), len(Envelope1))



ResultEnvelop = EnvelopeDecimated1 + EnvelopeDecimated2 + EnvelopeDecimated3 + EnvelopeDecimated4 + EnvelopeDecimated5 + EnvelopeDecimated6
CorrelationEnvelope=AutoCorrelation(ResultEnvelop,EnvelopeDecimated,MinBPM,MaxBPM)

print(len(ResultEnvelop))

[max_strength, max_pos]=maxwithpos(CorrelationEnvelope)
print(max_strength,max_pos)
print((60 * EnvelopeDecimated)/(max_pos))
BPMs = []
values = []
N=15

end = math.ceil((60 * EnvelopeDecimated) / (MinBPM))

start = math.ceil((60 * EnvelopeDecimated) / (MaxBPM))

CorrelationEnvelope = CorrelationEnvelope+abs(min(CorrelationEnvelope))

y=[]
for i in range(start,end):
  BPM = (60 * EnvelopeDecimated) / i
  BPMs.append(BPM)
  y.append(CorrelationEnvelope[i])

t2 = time.process_time()
print(t2-t1)
#BPMs = [60*EnvelopeDecimated/(i+1) for i in range(len(CorrelationEnvelope))]
#print(BPMs)
plt.plot(BPMs,y,c='r')
plt.xlabel("BPM")
plt.show()