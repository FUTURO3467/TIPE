import numpy as np
from scipy.spatial.distance import euclidean

def contiens_None(m):
    return m.beatspectrum is None or m.beatspectrum is None or m.zerocrossingrate is None or m.spectral_centroid is None

class Music:
    def __init__(self, path, genre, beat_spectrum, spectral_flux, zero_crossing_rate, spectral_centroid):
        self.path = path
        self.genre = genre
        self.beatspectrum = beat_spectrum
        self.spectralflux = spectral_flux
        self.zerocrossingrate = zero_crossing_rate
        self.spectral_centroid = spectral_centroid

    def dist(self, other):
        if contiens_None(self) or contiens_None(other): return 1e99
        SFdist = euclidean(self.spectralflux, other.spectralflux)
        BSdist = euclidean(self.beatspectrum, other.beatspectrum)
        ZCRdist = abs(self.zerocrossingrate-other.zerocrossingrate)
        scDist = abs(self.spectral_centroid-other.spectral_centroid)
        # *10 and /10 are there to set every distance to a scale of 1000 (give them the same weight)
        return SFdist + BSdist + ZCRdist + scDist

    def toJSONAble(self):
        return {"path":self.path, "genre":self.genre, "beatspectrum":self.beatspectrum, "spectralFlux":self.spectralflux.tolist(), "zerocrossingrate":self.zerocrossingrate, "spectral_centroid": self.spectral_centroid}

def MusicfromJSON(elem):
    path = elem["path"]
    genre = elem["genre"]
    beatspectrum = elem["beatspectrum"]
    spectralFlux = elem["spectralFlux"]
    zerocrossingrate = elem["zerocrossingrate"]
    spectral_centroid = np.float64(-1)
    if elem.__contains__("spectral_centroid"):
        spectral_centroid = elem["spectral_centroid"]
    return Music(path,genre,beatspectrum,spectralFlux,zerocrossingrate, spectral_centroid)






#Unused
class SpectralFluxOB:
    def __init__(self, max, mean, pics):
        self.max = max
        self.mean = mean
        self.pics = pics
    def dist(self, other):
        arrdist = 0
        for i in range(len(other.pics)):
            for j in range(len(self.pics)):
                arrdist+=(other.pics[i][0]-self.pics[j][0])**2 + (other.pics[i][1]-self.pics[j][1])**2
        return arrdist/((len(other.pics)*len(self.pics))*(10e11))

    def toJSONAble(self):
        return {"max":self.max, "mean":self.mean, "pics":self.pics}
