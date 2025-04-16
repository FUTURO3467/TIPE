class SpectralFluxOB:
    def __init__(self, max, mean, pics):
        self.max = max
        self.mean = mean
        self.pics = pics
    def dist(self, other):
        return 0
class Music:
    def __init__(self, path, genre, beatspectrum, spectralflux, zerocrossingrate):
        self.path = path
        self.genre = genre
        self.beatspectrum = beatspectrum
        self.spectralflux = spectralflux
        self.zerocrossingrate = zerocrossingrate
    def dist(self, other):
        return 0
