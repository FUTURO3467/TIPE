from __future__ import division
import numpy as np
from scipy.fft import fft
from numpy import abs, sum, linspace
from numpy.fft import rfft
import librosa
from scipy.stats import skew, kurtosis

from Classes import Classes

def zeroCrossingRate(arr, duration):
    res = 0
    for i in range(1,len(arr)):
        if arr[i] == 0 or (arr[i-1]*arr[i]) < 0:
            res+=1
    return np.float64(res/duration)

def normalized_FFT(data):
    return np.abs(fft(data))

def SpectralFlux(data, samplerate):
    S = np.abs(librosa.stft(data))
    flux = np.sqrt(np.sum(np.diff(S, axis=1)**2, axis=0))
    return np.array([
        np.mean(flux),
        np.std(flux),
        np.max(flux),
        np.median(flux),
        skew(flux),
        kurtosis(flux)
    ])
def SpectralFlux_Old(data):
    data = normalized_FFT(data)
    F = [0]
    max = (data[1]-data[0])**2
    min = (data[1]-data[0])**2
    tot = 0
    pics = []
    for i in range(1,len(data)):
        e=(data[i]-data[i-1])**2
        if e > max:
            max = e
        elif e < min:
            min = e
        tot += e
        if i != len(data)-1 and F[i-1] < e < (data[i+1]-data[i])**2:
            pics.append((np.float64(e),i))
        F.append(e)
    correctedpics = [[0,0]]
    for i in range(len(pics)):
        if pics[i][0] >= max/2:
            correctedpics.append(pics[i])
    mean = (tot/(len(data)-1))
    res = Classes.SpectralFluxOB(np.float64(max), np.float64(mean), correctedpics)
    #plt.plot([i for i in range(len(F))], F)
    #plt.show()
    return res

def spectral_centroid(data, sample_rate):
    spectrum = abs(rfft(data))

    normalized_spectrum = spectrum / sum(spectrum)
    normalized_frequencies = linspace(0, 1, len(spectrum))
    spectral_centroid_normalized = sum(normalized_frequencies * normalized_spectrum)

    nyquist_freq = sample_rate / 2
    spectral_centroid_hz = spectral_centroid_normalized * nyquist_freq
    print("Spectral Centroid (Hz):", spectral_centroid_hz)
    return np.float64(spectral_centroid_hz)