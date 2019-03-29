import sqlite3, os
import CacheUtils as cu

COMMON_ANALYSIS_FILENAME = "results/analysis.csv"
DB = "music_indexed.db"
TABLE = "annotation"


class ResultAnalyzer:

	def __init__(self, resultDict, audioTransName, hashprintTransName, testName):

		self.resultDict = resultDict
		self.audioTransName = audioTransName
		self.hashprintTransName = hashprintTransName

		
		self.testName = testName
		self.accuracy = [self.individualAccuracy(a) for a in self.resultDict.keys()]

		# self.testName = testName + "_vote"
		# self.accuracy = [self.voteAnalysis(a) for a in self.resultDict.keys()]

		self.totalQuery = sum([i[2] for i in self.accuracy])
		self.totalMaster = sum([i[3] for i in self.accuracy])

	# accuracy per query
	def calculateTotalAccuracy(self):
		if not self.totalQuery:
			return "NA"
		return sum([i[1]*i[2] for i in self.accuracy]) / float(self.totalQuery)

	# accuracy per artist
	def calculateMeanAccuracy(self):
		if not len(self.accuracy):
			return "NA"
		return sum([i[1] for i in self.accuracy]) / float(len(self.accuracy))


	def individualAccuracy(self, artist):

		results = self.resultDict[artist]
		total = len(results)
		correct = 0

		masterPath = os.path.join(self.audioTransName, \
			self.hashprintTransName, artist)
		nMaster = len(cu.listdir(masterPath))

		conn = sqlite3.connect(DB)
		c = conn.cursor()
		for song in results.keys():

			songID = song.split(".")[0].split("_")[0]
			best = results[song].split(".")[0].split("_")[0]
			print("[individualAccuracy] hashprint algorithm gets best match song id", \
				best, "for song", songID)

			sql = "select title_id from {tn} where id={sid};".\
				format(tn=TABLE, sid=best)
			print("[individualAccuracy] start query 1:", sql)
			c.execute(sql)
			bestTitleID = c.fetchall()[0][0]
			print("[individualAccuracy] best title id", bestTitleID)


			sql = "select title_id from {tn} where id={sid};".\
				format(tn=TABLE, sid=songID)
			print("[individualAccuracy] start query 2:", sql)
			c.execute(sql)
			titleID = c.fetchall()[0][0]
			print("[individualAccuracy] actual title id", titleID)
			if titleID == bestTitleID:
				correct += 1

		conn.close()

		if not total:
			accuracy = 0
		else:
			accuracy = float(correct) / total
		return artist, accuracy, total, nMaster

	def voteAnalysis(self, artist):

		results = self.resultDict[artist]
		correct = 0

		masterPath = os.path.join(self.audioTransName, \
			self.hashprintTransName, artist)
		nMaster = len(cu.listdir(masterPath))

		conn = sqlite3.connect(DB)
		c = conn.cursor()

		finalResults = dict()
		for song in results.keys():

			songID, ClipIndex = song.split(".")[0].split("_")
			best = results[song].split(".")[0].split("_")[0]
			print("[voteAnalysis] hashprint algorithm gets best match song id", \
				best, "for song", songID)

			if not finalResults.get(songID):
				votes = list()
				finalResults[songID] = votes
			else:
				votes = finalResults[songID]


			sql = "select title_id from {tn} where id={sid};".\
				format(tn=TABLE, sid=best)
			print("[voteAnalysis] start query 1:", sql)
			c.execute(sql)
			bestTitleID = c.fetchall()[0][0]
			print("[voteAnalysis] best title id", bestTitleID)

			votes.append(bestTitleID)

		for song in finalResults.keys():
			votes = finalResults[song]
			print("[voteAnalysis] song", song, "gets votes", votes)
			bestVote = max(votes,key=votes.count)
			print("[voteAnalysis] gets vote mode as", bestVote)

			sql = "select title_id from {tn} where id={sid};".\
				format(tn=TABLE, sid=song)
			print("[voteAnalysis] start query 2:", sql)
			c.execute(sql)
			titleID = c.fetchall()[0][0]
			print("[voteAnalysis] actual title id", titleID)
			if titleID == bestVote:
				correct += 1

		conn.close()

		total = len(finalResults)
		if not total:
			accuracy = 0
		else:
			accuracy = float(correct) / total
		return artist, accuracy, total, nMaster



	# save all information to path analysis_[audioTransName]_[hashprintTransName]_[testName].txt
	def saveAll(self):
		
		fileName = "results/analysis_{}_{}_{}.csv".format(\
			self.audioTransName, self.hashprintTransName, self.testName)
		with open(fileName, "w") as fd:
			fd.write("{},{},{},{}\n".format("total", self.calculateTotalAccuracy(), \
				self.totalQuery, self.totalMaster))
			fd.write("{},{},{},{}\n".format("total", self.calculateMeanAccuracy(), \
				len(self.accuracy), "NA"))
			for artist, acc, total, total2 in self.accuracy:
				fd.write("{},{},{},{}\n".format(artist, acc, total, total2))

		print("[saveAll] saved all analysis to", fileName)

	# save to a common csv file for comparison
	def saveToCommonCSV(self):

		with open(COMMON_ANALYSIS_FILENAME, "a") as fd:
			fd.write("{},{},{},{},{},{},{},{}\n".format(\
				self.audioTransName, self.hashprintTransName, self.testName, \
				self.calculateTotalAccuracy(), self.calculateMeanAccuracy(),
				self.totalQuery, self.totalMaster, len(self.accuracy)))
		print("[saveToCommonCSV] saved to common csv file", \
			self.audioTransName, self.hashprintTransName, self.testName)






