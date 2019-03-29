import audioread as ar
import CacheUtils as cu
import os

def clipAudio(dirPath, fileName, clip_len, max_clip):
	filePath = os.path.join(dirPath, fileName)
	audioID = fileName.split(".")[0]

	with ar.audio_open(filePath) as a:
		seconds = a.duration
		max_duration = int(min(seconds//clip_len, max_clip) * clip_len)

		
		for i in range(0,max_duration,clip_len):
			newFilePath = os.path.join(dirPath, "{}_{}.mp3".format(audioID, i))
			print("[clipAudio]",filePath,"from",i,"to",i+clip_len)
			os.system("ffmpeg -i {} -ss {} -t {} -acodec copy {}".\
				format(filePath, i, clip_len, newFilePath))
	os.system("rm {}".format(filePath))


def extendQueryByClip(test, version, clip_len=20, max_clip=10):
	print("[extendQueryByClip] extending", test, "to version", version)
	newTestName = "{}_{}".format(test, version)
	os.system("cp -r {} {}".format(test, newTestName))

	for artist in cu.listdir(newTestName):
		dirPath = os.path.join(newTestName, artist)
		for song in cu.listdir(dirPath):
			clipAudio(dirPath, song, clip_len, max_clip)


extendQueryByClip("live", "clip10", 10, 10)
extendQueryByClip("live", "clip20", 20, 10)
extendQueryByClip("live", "clip30", 30, 10)
extendQueryByClip("live", "clip40", 40, 10)


extendQueryByClip("cover", "clip10", 10, 10)
extendQueryByClip("cover", "clip20", 20, 10)
extendQueryByClip("cover", "clip30", 30, 10)
extendQueryByClip("cover", "clip40", 40, 10)












