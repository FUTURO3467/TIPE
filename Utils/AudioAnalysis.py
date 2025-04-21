import numpy as np
from scipy.fft import fft

from TIPE.Classes import Classes

def zeroCrossingRate(arr, duration):
    res = 0
    for i in range(1,len(arr)):
        if arr[i] == 0 or (arr[i-1]*arr[i]) < 0:
            res+=1
    return np.float64(res/duration)

def normalized_FFT(data):
    return np.abs(fft(data))

def SpectralFlux(data):
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
    correctedpics = []
    for i in range(len(pics)):
        if pics[i][0] >= max/2:
            correctedpics.append(pics[i])
    mean = (tot/(len(data)-1))
    res = Classes.SpectralFluxOB(np.float64(max), np.float64(mean), correctedpics)
    return res




