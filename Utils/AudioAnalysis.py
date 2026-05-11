from __future__ import division
import numpy as np
from numpy import abs, sum, linspace
from numpy.fft import rfft
import librosa
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
import audio2numpy as a2n
def frequence_annulation(tab, duree):
    res = 0
    for i in range(1, len(tab)):
        if tab[i] == 0 or (tab[i - 1] * tab[i]) < 0:
            res+=1
    return np.float64(res / duree)

def flux_spectral(donnees):
    S = np.abs(librosa.stft(donnees))
    flux = np.sqrt(np.sum(np.diff(S, axis=1)**2, axis=0))
    return np.array([
        np.mean(flux),
        np.std(flux),
        np.max(flux),
        np.median(flux),
        skew(flux),
        kurtosis(flux)
    ])

def centroid_spectral(données, fréquence_échantillonage):
    spectre = abs(rfft(données))
    spectre_normalisé = spectre / sum(spectre)
    frequences_normalisées = linspace(0, 1, len(spectre))
    centroid_spectral_normalisé = sum(frequences_normalisées * spectre_normalisé)
    nyquist_freq = fréquence_échantillonage / 2
    centroid_spectral_hz = centroid_spectral_normalisé * nyquist_freq
    print("Spectral Centroid (Hz):", centroid_spectral_hz)
    return np.float64(centroid_spectral_hz)

#NEXISTE PAS


def Dessine_Flux_Spectral(données):
    S = np.abs(librosa.stft(données))
    flux = np.sqrt(np.sum(np.diff(S, axis=1)**2, axis=0))
    print(len(S))
    fig, axs = plt.subplots(2)
    axs[0].plot(range(len(données)), données)
    axs[1].plot(range(len(flux)), flux)
    axs[0].set_title("Musique originale")
    axs[1].set_title("Flux spectral")
    plt.show()
    return np.array([
        np.mean(flux),
        np.std(flux),
        np.max(flux),
        np.median(flux),
        skew(flux),
        kurtosis(flux)
    ])
if __name__ == "__main__":
    path = r"D:\BDDTIPE\Tests\HipHop\It's Notherground Music!! - Future Music.mp3"
    data, samplerate = a2n.audio_from_file(path)
    if hasattr(data[0], "__len__"):
        data = data[:, 0]
    Dessine_Flux_Spectral(data)