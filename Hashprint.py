import numpy as np 
import librosa as la
import CacheUtils as cu
from runHashprint import MODEL


MODEL_HOP = 5
MODEL_TAO = 1
MODEL_FRAME = 20
MODEL_FEATURES = 64
MODEL_DELTADELAY = 16

class HashprintFunction:

	def __init__(self, transformFun, modelPath):
		self.transformFun = transformFun
		self.modelPath = modelPath

	def fun(self, audioPath):
		print("[hashprintFun] calculating hashprint at:", audioPath)
		spec = self.transformFun(audioPath)
		model = cu.loadNumpy(self.modelPath)

		tdeMatrix = getHashprintTDE(spec)
		features = np.matmul(np.transpose(tdeMatrix), model)

		deltas = features[:,:(np.size(features,1)-MODEL_DELTADELAY)] - \
			features[:,MODEL_DELTADELAY:];

		print("[hashprintFun] calculated hashprint of shape:", np.shape(deltas))

		return deltas > 0


def learnHashprintModel(specList):

	spectrograms = [cu.loadNumpy(spec) for spec in specList]

	matrixCov = 0
	for spec in spectrograms:
		matrixCov = np.add(matrixCov, np.cov(getHashprintTDE(spec)))

	matrixCovMean = np.divide(matrixCov, len(spectrograms))

	eigValue, eigVector = np.linalg.eig(matrixCovMean)

	eigPairs = list(zip(np.abs(eigValue).tolist(), np.transpose(eigVector).tolist()))
	sortedPairs = sorted(eigPairs, reverse=True, key=lambda p: p[0])
	features = np.transpose(np.array([pair[1] for pair in sortedPairs[:MODEL_FEATURES]]))
	print("[learnHashprintModel] learned model of shape", np.shape(features))

	return features


def getHashprintTDE(spec):
	nFrame = np.size(spec,1)
	nBin = np.size(spec,0)
	tdeSpan = MODEL_TAO * (MODEL_FRAME-1) + 1
	endIdx = nFrame - tdeSpan
	offsets = range(0, endIdx, MODEL_HOP)

	matrix = np.empty((len(offsets), nBin * MODEL_FRAME))

	for i in range(MODEL_FRAME):
		frameIdxs = [off + i * MODEL_TAO for off in offsets];
		matrix[:,(i*nBin):(i+1)*nBin] = np.transpose(spec[:,frameIdxs])
	rv = np.transpose(matrix)

	print("[getHashprintTDE] calculated TDE of size", np.shape(rv))
	return rv

def runHashprintQuery(queryPath, hashprintDB):

	queryData = cu.loadNumpy(queryPath)

	print("[runHashprintQuery] receive query data of shape:", np.shape(queryData))

	queryLen = len(queryData)

	scores = list()

	for song in hashprintDB.keys():

		print("[runHashprintQuery] run data against song:", song)

		songScores = list()
		for hashprint in hashprintDB[song]:
			hashLen = len(hashprint)

			if queryLen < hashLen:
				songScores.append(hashprintMatchScore(queryData, hashprint))
			else:
				songScores.append(hashprintMatchScore(hashprint, queryData))

		best = min(songScores)
		print("[runHashprintQuery] get min score:", best)
		scores.append((best, song))

	scores.sort()
	print("[runhashprintQuery] best choice overall:", scores[0])
	return scores[0][1]


def hashprintMatchScore(hp1, hp2):
	
	hpLen = len(hp1)

	if hpLen == len(hp2):
		best = np.sum(np.logical_xor(hp1, hp2))
	else:
		scoreList = list()
		for i in range(len(hp2)-hpLen):
			scoreList.append(np.sum(np.logical_xor(hp1, hp2[i:hpLen+i])))
		best = min(scoreList)
	print("[hashprintMatchScore] comparing shape {} against {} gets {}".format(\
		np.shape(hp1), np.shape(hp2), best))

	return best














