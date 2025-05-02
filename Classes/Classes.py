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
        return [self.max, self.mean, self.pics]
class Music:
    def __init__(self, path, genre, beatspectrum, spectralflux, zerocrossingrate):
        self.path = path
        self.genre = genre
        self.beatspectrum = beatspectrum
        self.spectralflux = spectralflux
        self.zerocrossingrate = zerocrossingrate
    def dist(self, other):
        SFdist = self.spectralflux.dist(other.spectralflux)
        arrdist = 0
        for i in range(len(other.beatspectrum)):
            for j in range(len(self.beatspectrum)):
                arrdist+=(other.beatspectrum[i][0]-self.beatspectrum[j][0])**2 + (other.beatspectrum[i][1]-self.beatspectrum[j][1])**2
        arrdist = arrdist/(len(other.beatspectrum)*len(self.beatspectrum))
        ZCRdist = abs(self.zerocrossingrate-other.zerocrossingrate)
        return SFdist + arrdist + ZCRdist
    def toJSONAble(self):
        return [self.path, self.genre, self.beatspectrum, self.spectralflux.toJSONAble(), self.zerocrossingrate]
