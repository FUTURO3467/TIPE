import numpy as np
from scipy.spatial.distance import euclidean
from math import sqrt

def contiens_None(m):
    return m.beatspectrum is None or m.beatspectrum is None or m.frequenceannulation is None or m.centroide_spectral is None

class Music:
    def __init__(self, chemin, genre, beat_spectrum, fluxspectral, frequenceannulation, centroide_spectral):
        self.chemin = chemin
        self.genre = genre
        self.beatspectrum = beat_spectrum
        self.fluxspectral = fluxspectral
        self.frequenceannulation = frequenceannulation
        self.centroide_spectral = centroide_spectral

    def dist(self, other):
        if contiens_None(self) or contiens_None(other): return 1e99
        SFdist = euclidean(self.fluxspectral, other.fluxspectral) * 10
        BSdist = euclidean(self.beatspectrum, other.beatspectrum)/10
        ZCRdist = abs(self.frequenceannulation - other.frequenceannulation)
        scDist = abs(self.centroide_spectral - other.centroide_spectral)
        return sqrt(SFdist*SFdist + BSdist*BSdist + ZCRdist*ZCRdist + scDist*scDist)

    def toJSONAble(self):
        return {"path":self.chemin,
                "genre":self.genre,
                "beatspectrum":self.beatspectrum,
                "spectralFlux":self.fluxspectral.tolist(),
                "zerocrossingrate":self.frequenceannulation,
                "spectral_centroid": self.centroide_spectral}

def MusicfromJSON(elem):
    chemin = elem["path"]
    genre = elem["genre"]
    beatspectrum = elem["beatspectrum"]
    fluxspectral = elem["spectralFlux"]
    frequenceannulation = elem["zerocrossingrate"]
    centroide_spectral = np.float64(-1)
    if elem.__contains__("spectral_centroid"):
        centroide_spectral = elem["spectral_centroid"]
    return Music(chemin,genre,beatspectrum,fluxspectral,frequenceannulation, centroide_spectral)
