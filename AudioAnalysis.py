
def zeroCrossingRate(arr, duration):
    res = 0
    for i in range(1,len(arr)):
        if arr[i] == 0 or (arr[i-1]*arr[i]) < 0:
            res+=1
    return res/duration