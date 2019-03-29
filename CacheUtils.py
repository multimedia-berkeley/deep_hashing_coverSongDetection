import numpy as np
import librosa as la
import os

NUMPY_SUFFIX = ".npy"


def listdir(path):
	return [p for p in os.listdir(path) if p[0] != '.']

# save given numpy object with the name filePrefix.npy, in the given directory
def saveNumpy(obj, filePrefix, direPath):
	print("[saveNumpy] saving numpy shape:", np.shape(obj))
	if not os.path.exists(direPath):
		os.makedirs(direPath)
	filePath = os.path.join(direPath, filePrefix + NUMPY_SUFFIX)
	with open(filePath, "wb") as fd:
		np.save(fd, obj)
		print("[saveNumpy] saved", filePath)

# load the saved numpy object at given fileName
def loadNumpy(fileName):
	print("[loadNumpy] loading", fileName)
	return np.load(fileName)

# load the database stored in the path
# the path should contain only saved hashprint files
def loadHashprintDB(dbPath):
	
	print("[loadHashprintDB] loading db at path", dbPath)
	database = dict()
	for song in listdir(dbPath):
		database[song] = [np.load(os.path.join(dbPath,song,p)) \
			for p in os.listdir(os.path.join(dbPath,song))]

	return database



def saveWAV(filePath, audio, sr):
	print("[saveWAV] saved", filePath)
	la.output.write_wav(filePath, audio, sr)

	


