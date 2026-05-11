import matplotlib.pyplot as plt
import scipy.signal as sig
import math
import pydub
import threading
import numpy as np
from scipy.stats import skew, kurtosis, entropy
from scipy.signal import find_peaks
import audio2numpy as a2n

def read(f, normalized=False):
    a = pydub.AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2 ** 15
    else:
        return a.frame_rate, y


def beatspectrum_features(hist, bpms):
    hist = np.array(hist, dtype=float)
    bpms = np.array(bpms, dtype=float)
    hist = np.maximum(hist, 1e-12)
    H = np.sum(hist)
    N = len(hist)
    moyenne = np.mean(hist)
    ecart_type = np.std(hist)
    skewness = skew(hist)
    kurt = kurtosis(hist)
    max = np.max(hist)
    max_bpm = np.argmax(hist)
    #entropie
    p = hist / H
    f_entropy = entropy(p)
    peaks, _ = find_peaks(hist)
    peak_values = hist[peaks]
    #on complète si pas assez de pics
    if len(peaks) < 2:
        peaks = np.append(peaks, max_bpm)
        peak_values = np.append(peak_values, hist[max_bpm] * 0.0001)
    #ratio premier pic / second pic
    #trier les pics par amplitude
    top2_indices = np.argsort(peak_values)[-2:]
    p1, p2 = 0, 0
    idx_p1, idx_p2 = 0, 0
    if len(top2_indices) >= 2:
        p1, p2 = peak_values[top2_indices[1]], peak_values[top2_indices[0]]
        idx_p1, idx_p2 = peaks[top2_indices[1]], peaks[top2_indices[0]]
    elif len(top2_indices) == 1:
        p2 = peak_values[top2_indices[0]]
        idx_p1 = peaks[top2_indices[0]]
    f_ratio12 = p1 / p2 if p2 != 0 else 1e99
    #BPM du second pic
    f_bpm2 = bpms[idx_p2]
    #distance moyenne pondérée au pic principal
    indices = np.arange(N)
    f_width = np.sum(np.abs(indices - max_bpm) * hist) / H
    #Applatissement
    geo_mean = np.exp(np.mean(np.log(hist)))
    f_flatness = geo_mean / moyenne
    #Densité de pics
    f_peak_density = len(peaks) / N
    #Variabilité locale des pics
    f_lpv = np.var(peak_values)
    return [float(f) for f in
                [
                moyenne,
                ecart_type,
                skewness,
                kurt,
                max,
                float(max_bpm),
                f_entropy,
                f_ratio12,
                f_bpm2,
                f_width,
                f_flatness,
                f_peak_density,
                f_lpv
                ]
            ]

def mean(a):
    tot = 0
    l = len(a)
    for i in range(l):
        tot += a[i]
    return (tot / l)

def getpos(e, a):
    for i in range(len(a)):
        if a[i] == e:
            return i
    return -1

def AutoCorrelation(envelope, EnvelopeDecimated, MinBPM, MaxBPM, n=6):
    fin = math.ceil((60 * EnvelopeDecimated) / (MinBPM))
    debut = math.ceil((60 * EnvelopeDecimated) / (MaxBPM))
    ts = len(envelope) - fin
    xc = np.zeros(fin)
    for i in range(debut, fin):
        sum = 0
        for j in range(1, ts):
            sum += (envelope[j] * envelope[j + i])
        xc[i] += sum
    return xc


def SubBandDWT(Signal, Fs, L, H):
    LowFrequencyBand = L / (Fs / 2)
    [numerator, denominator] = sig.butter(2, LowFrequencyBand, 'high')
    if hasattr(Signal[0], "__len__"):
        Signal = Signal[:, 0]
    FiltredSignal = sig.filtfilt(numerator, denominator, Signal)
    HighFrequencyBand = H / (Fs / 2)
    [numerator, denominator] = sig.butter(2, HighFrequencyBand, 'low')
    SubBand = sig.filtfilt(numerator, denominator, FiltredSignal)
    return [SubBand, numerator, denominator]


def Envelope(SubBand, DecimateValue, new_fs, numerator, denominator):
    SubBand = abs(SubBand)
    bande_passebas = sig.filtfilt(numerator, denominator, SubBand)
    bands = sig.decimate(bande_passebas, DecimateValue)
    m = mean(bands)
    enlever_moyenne = bands - m
    Tw = 0.1
    Nw = Tw * new_fs
    w = np.ones(int(Nw)) / Nw
    enevelope_rectifiée = np.convolve(enlever_moyenne, w, 'same')
    return enevelope_rectifiée

Envelope1 = []
Envelope2 = []
Envelope3 = []
Envelope4 = []
Envelope5 = []
Envelope6 = []
def BeatSpectrum(data, samplerate):
    # Paramètres
    MinBPM = 40
    MaxBPM = 200

    new_fs = 22050
    EnvelopeDecimated = 200
    t = np.arange(len(data)) / float(samplerate)
    print(len(data))

    DecimateValue = math.ceil(samplerate / new_fs)
    def EnvelopeCalc(n):
        if n == 1:
            [SubBand1, numerator1, denominator1] = SubBandDWT(data, samplerate, 1, 200)
            global Envelope1
            Envelope1 = Envelope(SubBand1, DecimateValue, new_fs, numerator1, denominator1)
        elif n == 2:
            [SubBand2, numerator2, denominator2] = SubBandDWT(data, samplerate, 200, 400)
            global Envelope2
            Envelope2 = Envelope(SubBand2, DecimateValue, new_fs, numerator2, denominator2)
        elif n == 3:
            [SubBand3, numerator3, denominator3] = SubBandDWT(data, samplerate, 400, 800)
            global Envelope3
            Envelope3 = Envelope(SubBand3, DecimateValue, new_fs, numerator3, denominator3)
        elif n == 4:
            [SubBand4, numerator4, denominator4] = SubBandDWT(data, samplerate, 800, 1600)
            global Envelope4
            Envelope4 = Envelope(SubBand4, DecimateValue, new_fs, numerator4, denominator4)
        elif n == 5:
            [SubBand5, numerator5, denominator5] = SubBandDWT(data, samplerate, 1600, 3200)
            global Envelope5
            Envelope5 = Envelope(SubBand5, DecimateValue, new_fs, numerator5, denominator5)
        else:
            [SubBand6, numerator6, denominator6] = SubBandDWT(data, samplerate, 3200, 6400)
            global Envelope6
            Envelope6 = Envelope(SubBand6, DecimateValue, new_fs, numerator6, denominator6)


    c = math.floor((samplerate / DecimateValue) / EnvelopeDecimated)
    ts = []
    for i in range(6):
        t = threading.Thread(target=EnvelopeCalc, args=(i+1,))
        t.start()
        ts.append(t)

    for i in range(6):
        ts[i].join()
    global Envelope1
    global Envelope2
    global Envelope3
    global Envelope4
    global Envelope5
    global Envelope6
    EnvelopeDecimated1 = [Envelope1[i * c] for i in range(int(len(Envelope1) / c))]
    EnvelopeDecimated2 = [Envelope2[i * c] for i in range(int(len(Envelope2) / c))]
    EnvelopeDecimated3 = [Envelope3[i * c] for i in range(int(len(Envelope3) / c))]
    EnvelopeDecimated4 = [Envelope4[i * c] for i in range(int(len(Envelope4) / c))]
    EnvelopeDecimated5 = [Envelope5[i * c] for i in range(int(len(Envelope5) / c))]
    EnvelopeDecimated6 = [Envelope6[i * c] for i in range(int(len(Envelope6) / c))]
    ResultEnvelop = (EnvelopeDecimated1+
                     EnvelopeDecimated2+
                     EnvelopeDecimated3+
                     EnvelopeDecimated4+
                     EnvelopeDecimated5+
                     EnvelopeDecimated6)
    CorrelationEnvelope = AutoCorrelation(ResultEnvelop, EnvelopeDecimated, MinBPM, MaxBPM)

    BPMs = []
    end = math.ceil((60 * EnvelopeDecimated) / (MinBPM))
    start = math.ceil((60 * EnvelopeDecimated) / (MaxBPM))
    CorrelationEnvelope = CorrelationEnvelope + abs(min(CorrelationEnvelope))

    y = []
    for i in range(start, end):
        BPM = (60 * EnvelopeDecimated) / i
        BPMs.append(BPM)
        y.append(CorrelationEnvelope[i])
    plt.plot(BPMs,y)
    plt.xlabel("BPM")
    plt.ylabel("Amplitude")
    plt.title("Spectre de Pulsations")
    plt.show()
    return beatspectrum_features(y, BPMs)

if __name__ == "__main__":
    path = r"D:\BDDTIPE\Tests\HipHop\It's Notherground Music!! - Future Music.mp3"
    data, samplerate = a2n.audio_from_file(path)
    BeatSpectrum(data, samplerate)