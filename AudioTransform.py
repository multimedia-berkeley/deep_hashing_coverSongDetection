import numpy as np 
import librosa as la
import CacheUtils as cu
import random

STANDARD_SAMPLE_RATE = 22050

class CQT_LIBROSA:

    def __init__(self, sr=STANDARD_SAMPLE_RATE, nbin=96, hopLength=96,
    binPerOctave=12, downsample=3, groupSize=1):

        self.sr = sr
        self.nbin = nbin
        self.hopLength = hopLength
        self.binPerOctave = binPerOctave
        self.downsample = downsample
        self.groupSize = groupSize


    def fun(self, filename):
        y, sr2 = la.load(filename, sr=self.sr)
        cqt = la.core.cqt(y, n_bins=self.nbin, 
            bins_per_octave=self.binPerOctave,real=False)
        cqt_log = np.log(1 + 1000000 * cqt)
        print("[CQT_LIBROSA] final output spec size:", np.shape(cqt_log))
        return cqt_log



class CQT_LIBROSA_NOLOG:

    def __init__(self, sr=STANDARD_SAMPLE_RATE, nbin=96, hopLength=96,
    binPerOctave=12, downsample=3, groupSize=1):

        self.sr = sr
        self.nbin = nbin
        self.hopLength = hopLength
        self.binPerOctave = binPerOctave
        self.downsample = downsample
        self.groupSize = groupSize


    def fun(self, filename):
        y, sr2 = la.load(filename, sr=self.sr)
        cqt = la.core.cqt(y, n_bins=self.nbin, 
            bins_per_octave=self.binPerOctave, real=False)
        print("[CQT_LIBROSA] final output spec size:", np.shape(cqt))
        return cqt



class CQT_TJ:

    def __init__(self, sr=44100, nbin=121, hopLength=96, 
    binPerOctave=24, downsample=3, groupSize=1):

        self.sr = sr
        self.nbin = nbin
        self.hopLength = hopLength
        self.binPerOctave = binPerOctave
        self.downsample = downsample
        self.groupSize = groupSize

    def fun(self, filename):

        try:
            y, sr2 = la.load(filename, sr=self.sr, mono=False)
            y = la.resample(np.sum(y,0), 
                orig_sr=self.sr, target_sr=STANDARD_SAMPLE_RATE)
            cqt = la.core.cqt(y,bins_per_octave=self.binPerOctave, 
                n_bins=self.nbin, sr=STANDARD_SAMPLE_RATE, 
                hop_length=self.hopLength, real=False)
        except:
            y, sr2 = la.load(filename, sr=STANDARD_SAMPLE_RATE)
            cqt = la.core.cqt(y,bins_per_octave=self.binPerOctave, 
                n_bins=self.nbin, sr=STANDARD_SAMPLE_RATE, 
                hop_length=self.hopLength, real=False)

        nBin = np.size(cqt,0)
        nChunk = np.size(cqt,1) // (self.downsample * self.groupSize)
        cqt = np.abs(cqt[:,:self.downsample * self.groupSize * nChunk])
        cqt = np.reshape(cqt, (nBin, self.downsample, nChunk * self.groupSize))
        cqt = np.mean(cqt, 1)
        cqt = np.reshape(cqt, (nBin, nChunk * self.groupSize))
        cqt = np.reshape(cqt, (nBin * self.groupSize, nChunk))
        cqt_log = np.log(1 + 1000000 * cqt)

        print("[CQT_TJ] final output spec size:", np.shape(cqt_log))

        return cqt_log


class PITCH_SHIFT:

    def __init__(self, nPitch=4, sr=STANDARD_SAMPLE_RATE, binPerOctave=24):
        self.nPitch = nPitch
        self.sr = sr
        self.binPerOctave = binPerOctave

    def fun(self, filename):
        audio, sr2 = la.load(filename, sr=self.sr)
        changes = list(range(-self.nPitch,0)) + list(range(1, self.nPitch+1))
        specs = [la.effects.pitch_shift(audio, \
            sr=self.sr, n_steps=i, bins_per_octave=self.binPerOctave) \
            for i in changes]
        print("[PITCH_SHIFT] generated additional {} samples".format(len(specs)))

        names = list()
        randomID = random.getrandbits(32)
        for i in range(len(specs)):
            name = "temp_PITCH_SHIFT_{}_{}.wav".format(i,randomID)
            cu.saveWAV(name, specs[i], self.sr)
            names.append(name)
        return names



class TIME_STRETCH:

    def __init__(self, maxStretch=2, interval=0.2, 
        sr=STANDARD_SAMPLE_RATE, binPerOctave=24):

        self.maxStretch = maxStretch
        self.interval = interval
        self.sr = sr
        self.binPerOctave = binPerOctave

    def fun(self, filename):
        audio, sr2 = la.load(filename, sr=self.sr)
        changes = [float(i) * self.interval for i in \
            range(1,int(self.maxStretch/self.interval))]
        specs = [la.effects.time_stretch(audio, rate=i) for i in changes]

        print("[TIME_STRETCH] generated additional {} samples".format(len(specs)))

        names = list()
        randomID = random.getrandbits(32)
        for i in range(len(specs)):
            name = "temp_TIME_STRETCH_{}_{}.wav".format(i, randomID)
            cu.saveWAV(name, specs[i], self.sr)
            names.append(name)
        return names
















