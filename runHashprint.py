import AudioTransform as at
import Hashprint as hp
import CacheUtils as cu
import testMap as tm
import ResultAnalysis as ra
import os, sqlite3, sys, random

MASTER = "master"
MODEL = "model"

artistList = cu.listdir(MASTER)

# transform the addios in given folder using the given audio transform function
# the transform function should take in a audio and output a numpy spectrogram
# the numpy will be saved in the same structure in transformName/folder
def transformAll(folder, audioTransName, audioTransFun):
	print("[transformAll] start at folder:", folder)
	removed = list()
	for artist in artistList:
		print("[transformAll] artist:", artist)
		for song in cu.listdir(os.path.join(folder, artist)):
			print("[transformAll] song:", song)
			try:
				songPath = os.path.join(folder, artist, song)
				spectrogram = audioTransFun(songPath)
				cu.saveNumpy(spectrogram, song, os.path.join(audioTransName, folder, artist))
			except:
				print("[transformAll][ERROR] trnasformation failed for song:", song)
				print("[transformAll][ERROR] imcomplete master, remove artist", artist)
				removed.append(artist)
				break
		
		# if not os.path.exists(os.path.join(audioTransName, folder, artist)):

	for r in removed:
		artistList.remove(r)
		if os.path.exists(os.path.join(audioTransName, folder, artist)):
			os.system("rm -rf {}".format(os.path.join(audioTransName, folder, artist)))
		print("[transformAll][ERROR] removed artist", r)




# calculate all hashprints in a given folder
def calculateHashprintAll(folder, key, audioTransFun):

	print("[calculateHashprintAll] start at folder:", folder)
	for artist in artistList:
		modelPath = os.path.join(key, MODEL, artist + cu.NUMPY_SUFFIX)
		hashprintFun = hp.HashprintFunction(audioTransFun, modelPath).fun
		print("[calculateHashprintAll] artist:", artist)
		for song in cu.listdir(os.path.join(folder, artist)):
			try:
				print("[calculateHashprintAll] song:", song)
				songPath = os.path.join(folder, artist, song)
				hashprint = hashprintFun(songPath)
				cu.saveNumpy(hashprint, song, os.path.join(key, folder, artist))
			except:
				print("[calculateHashprintAll][ERROR] hashprint calculation failed for song:", song)

# make hashprint models given the transformation and associated model generating function
# each model is an array of eigenvectors, and will be saved in transformName/model
def makeModels(audioTransName):

	transMaster = os.path.join(audioTransName, MASTER)
	print("[makeModels] start at folder:", transMaster)

	for artist in artistList:
		print("[makeModels] artist:", artist)
		specList = [os.path.join(transMaster, artist, spec) \
			for spec in cu.listdir(os.path.join(transMaster, artist))]

		model = hp.learnHashprintModel(specList)
		cu.saveNumpy(model, artist, os.path.join(audioTransName, MODEL))


# make complete hashprint databases given audio transformation and hashprint transformation
# each hashprint transform funciton takes a spectrogram and output a series of transformations
# then hash function is applied to each of them to compute a list of hashprints for each audio
def makeDatabases(audioTransName, hashprintTransName):

	print("[makeDatabases] start at folder:", MASTER)

	for artist in artistList:

		print("[makeDatabases] artist:", artist)

		modelPath = os.path.join(audioTransName, MODEL, artist + cu.NUMPY_SUFFIX)
		hashprintFun = hp.HashprintFunction(\
			tm.AUDIO_TRANS_MAP[audioTransName], modelPath).fun

		for song in cu.listdir(os.path.join(MASTER, artist)):

			print("[makeDatabases] song:", song)
			songPath = os.path.join(MASTER, artist, song)
			savePath = os.path.join(audioTransName, hashprintTransName, artist, song)
			
			try:
				songList = tm.HP_TRANS_MAP[hashprintTransName](songPath)
				hashprintList = [hashprintFun(s) for s in songList]

				for s in songList:
					os.system("rm -f {}".format(s))

				for i in range(len(hashprintList)):
					saveName = "hashprint_{}_{}_{}_{}_{}".format(\
						audioTransName, hashprintTransName, artist, song, i)
					cu.saveNumpy(hashprintList[i], saveName, savePath)
			except:
				print("[makeDatabases][ERROR] cannot make hashprint series for song",song)
				print("[makeDatabases][ERROR] remove artist {} in database {}".\
					format(artist, song))
				artistPath = os.path.join(audioTransName,hashprintTransName,artist)
				if os.path.exists(artistPath):
					os.system("rm -rf {}".format(artistPath))
				break





# run query of each query hashprint against a precomputed database
# returns a dictionary of results corresponding to each artist
# each artist produces results of their corresponding queries
# the two level dict is returned for detailed analysis
def runQueryAnalysis(audioTransName, hashprintTransName, testName):

	print("[runQueryAnalysis] start analysis of:", \
		audioTransName, hashprintTransName, testName)

	testPath = os.path.join(audioTransName, testName)
	dbsPath = os.path.join(audioTransName, hashprintTransName)
	
	resultDict = dict()

	for artist in cu.listdir(os.path.join(audioTransName, hashprintTransName)):

		print("[runQueryAnalysis] start artist:", artist)

		artistResult = dict()
		hashprintDB = cu.loadHashprintDB(os.path.join(dbsPath, artist))

		for songHashprint in cu.listdir(os.path.join(testPath, artist)):

			songHashprintPath = os.path.join(testPath, artist, songHashprint)
			artistResult[songHashprint] = hp.runHashprintQuery(songHashprintPath, hashprintDB)

		resultDict[artist] = artistResult

	analysis = ra.ResultAnalyzer(resultDict, audioTransName, hashprintTransName, testName)
	analysis.saveAll()
	analysis.saveToCommonCSV()


def mainForEachKey(key):

	# for each type of audio transformation, if have not computed hashprint database:
	# 	1. compute given transformation for each artist each song
	#	2. compute model using the computed transformation
	#	3. for each type of hashprint transformation, compute database

	print("[main] start constructing hashprint databases for:", key)

	if not os.path.exists(key):

		masterPath = os.path.join(key, MASTER)
		os.makedirs(masterPath)
		print("[main] add path:", masterPath)

		transformAll(MASTER, key, tm.AUDIO_TRANS_MAP[key])

		modelPath = os.path.join(key, MODEL)
		os.makedirs(modelPath)
		print("[main] add path:", modelPath)
		makeModels(key)

		for hpkey in tm.HP_TRANS_MAP.keys():

			hashprintPath = os.path.join(key, hpkey)
			os.makedirs(hashprintPath)
			print("[main] add path:", hashprintPath)

			makeDatabases(key, hpkey)


	else:
		print("[main] audio transfer type db detected for:",
			key, ", start search")

	# compute query result:
	# 	1. if have not compute the hashprint of test set, compute hashprint
	# 		* this only depends on the audio transformation calculated model
	# 	2. for each hashprint transformation, conduct query and analyze result
	print("[main] start querying databases")
	for test in tm.TESTS:
		print("[main] test for type:", test)
		testPath = os.path.join(key, test)
		modelPath = os.path.join(key, MODEL)

		if not os.path.exists(testPath):

			calculateHashprintAll(test, key, tm.AUDIO_TRANS_MAP[key])

		for hpkey in tm.HP_TRANS_MAP.keys():
			runQueryAnalysis(key, hpkey, test)

	# master cache is too big to store and useless, so delete when complete
	print("[main] deleting extra cache for databases for:", key)
	os.system("rm -rf {}/{}".format(key,MASTER))

	# except:
	# 	print("[ERROR] encounters error during trnasformation", key)
	# 	print("[ERROR] deleting all data")
	# 	os.system("rm -rf {}".format(key))
			
				
def main():
	try:
		testID = int(sys.argv[1])
		testKey = tm.TEST_MAP[testID]
		mainForEachKey(testKey)

	except Exception as e:
		print("[ERROR] Unexpected exception occured:")
		print(e)



if __name__ == '__main__':
	main()












