import scipy.signal as sig
import numpy as np
import math
import pydub
import threading

"""MP3 to numpy array"""
def read(f, normalized=False):
    a = pydub.AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2 ** 15
    else:
        return a.frame_rate, y


import numpy as np
from scipy.stats import skew, kurtosis, entropy
from scipy.signal import find_peaks


def beatspectrum_features(hist, bpms):
    """
    hist  : tableau d'amplitudes du Beat Spectrum (ex: ton y)
    bpms  : tableau des BPM correspondants (ex: ton BPMs)

    Retourne un vecteur de 20 features.
    """

    hist = np.array(hist, dtype=float)
    bpms = np.array(bpms, dtype=float)

    hist = np.maximum(hist, 1e-12)
    H = np.sum(hist)
    N = len(hist)

    # ---- 1. mean ----
    f_mean = np.mean(hist)

    # ---- 2. std ----
    f_std = np.std(hist)

    # ---- 3. skewness ----
    f_skew = skew(hist)

    # ---- 4. kurtosis ----
    f_kurt = kurtosis(hist)

    # ---- 5. max amplitude ----
    f_max = np.max(hist)

    # ---- 6. index du pic principal ----
    idx1 = np.argmax(hist)

    # ---- 7. somme totale ----
    f_sum = H

    # ---- 8. entropie ----
    p = hist / H
    f_entropy = entropy(p)

    # ---- Trouver tous les pics locaux ----
    peaks, _ = find_peaks(hist)
    peak_values = hist[peaks]

    # S’il n'y a pas assez de pics, on complète
    if len(peaks) < 2:
        # fabriquer un second pic fictif ultra faible
        peaks = np.append(peaks, idx1)
        peak_values = np.append(peak_values, hist[idx1] * 0.0001)

    # ---- 9. ratio premier pic / second pic ----
    # trier les pics par amplitude
    top2_indices = np.argsort(peak_values)[-2:]
    p1, p2 = peak_values[top2_indices[1]], peak_values[top2_indices[0]]
    idx_p1, idx_p2 = peaks[top2_indices[1]], peaks[top2_indices[0]]

    f_ratio12 = p1 / p2 if p2 != 0 else 0

    # ---- 10. index du second pic ----
    # (le second le plus haut)
    f_idx2 = idx_p2

    # ---- 11. deuxième amplitude (autocorr secondaire) ----
    f_second_amp = p2

    # ---- 12. energy compactness ----
    f_compactness = f_max / H

    # ---- 13. periodicity index ----
    f_periodicity = f_max / f_mean

    # ---- 14. BPM pic principal ----
    f_bpm1 = bpms[idx1]

    # ---- 15. BPM second pic ----
    f_bpm2 = bpms[idx_p2]

    # ---- 16. histogram width (largeur) ----
    # distance moyenne pondérée au pic principal
    indices = np.arange(N)
    f_width = np.sum(np.abs(indices - idx1) * hist) / H

    # ---- 17. sparsity ----
    # sqrt(N) * ||hist||_2 / ||hist||_1
    f_sparsity = np.sqrt(N) * (np.linalg.norm(hist, 2) / np.linalg.norm(hist, 1))

    # ---- 18. flatness ----
    geo_mean = np.exp(np.mean(np.log(hist)))
    f_flatness = geo_mean / f_mean

    # ---- 19. peak density ----
    f_peak_density = len(peaks) / N

    # ---- 20. local peak variability ----
    f_lpv = np.var(peak_values)

    # Regroupe tout dans un vecteur le float(f) est pour la transformation en JSON
    return [float(f) for f in
                [
                f_mean,
                f_std,
                f_skew,
                f_kurt,
                f_max,
                float(idx1),
                f_sum,
                f_entropy,
                f_ratio12,
                float(f_idx2),
                f_second_amp,
                f_compactness,
                f_periodicity,
                f_bpm1,
                f_bpm2,
                f_width,
                f_sparsity,
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


def maxwithpos(a):
    m = max(a)
    mi = 0
    for i in range(len(a)):
        if a[i] == m:
            mi = i
    return [m, mi]


def getpos(e, a):
    for i in range(len(a)):
        if a[i] == e:
            return i
    return -1

xc = []


def PartialAutoCorrelationCalculation(envelope,ts, start, end):
    for i in range(start, end):
        sum = 0
        for j in range(1, ts):
            sum += (envelope[j] * envelope[j + i])
        xc[i] += sum

def inflexion_points(arr, mspace):
    m = mean(arr)
    res = []
    i = 1
    while i < len(arr)-1:
        if arr[i-1] < arr[i] > arr[i+1] and arr[i] >= m:
            res.append(arr[i])
            i+=mspace
        i+=1
    return res



def AutoCorrelation(envelope, EnvelopeDecimated, MinBPM, MaxBPM, n=6):
    end = math.ceil((60 * EnvelopeDecimated) / (MinBPM))

    start = math.ceil((60 * EnvelopeDecimated) / (MaxBPM))

    ts = len(envelope) - end

    dist = end-start
    #t1 = time.process_time()

    global xc
    xc = np.zeros(end)
    tarr = []
    for i in range(1,n+1):
        t = threading.Thread(target=PartialAutoCorrelationCalculation, args=(envelope,ts, start + (dist//n)*(i-1), start + (dist//n)*i))
        t.start()
        tarr.append(t)
    for i in range(n):
        tarr[i].join()
    #for i in range(start, end):
    #    sum = 0
    #    for j in range(1, ts):
    #        sum += (envelope[j] * envelope[j + i])
    #    xc[i] += sum
    #print(time.process_time()-t1)
    return xc


def SubBandDWT(Signal, Fs, L, H):
    LowFrequencyBand = L / (Fs / 2);

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
    LowPassSubBand = sig.filtfilt(numerator, denominator, SubBand)

    bands = sig.decimate(LowPassSubBand, DecimateValue)
    m = mean(bands)
    MeanRemoval = bands - m

    Tw = 0.1
    Nw = Tw * new_fs
    w = np.ones(int(Nw)) / Nw

    RectifiedEnvelope = np.convolve(MeanRemoval, w, 'same')
    return RectifiedEnvelope

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

    ResultEnvelop = EnvelopeDecimated1 + EnvelopeDecimated2 + EnvelopeDecimated3 + EnvelopeDecimated4 + EnvelopeDecimated5 + EnvelopeDecimated6
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
    return beatspectrum_features(y, BPMs)