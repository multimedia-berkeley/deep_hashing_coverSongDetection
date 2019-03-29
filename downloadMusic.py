# -*- coding: utf-8 -*- 

import sqlite3, os

DB = "music_indexed.db"
TABLE = "annotation"
LEAST_MASTER_SIZE = 5

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("select distinct artist_id from {}".format(TABLE))
artists = [r[0] for r in c.fetchall()]

for artist in artists:

	# first download master pieces
	# if no master piece, no need to download live and cover ones
	# otherwise record all master titles, later downloads need to be in this set
	constraint = ("soundsrc in (0,1)", "master")
	print("[downloadMusic] Start download MASTER music for", artist)

	artistDir = constraint[1] + "/" + str(artist)
	coverDir = "cover" + "/" + str(artist)

	if not os.path.exists(artistDir):
		os.makedirs(artistDir)
		os.makedirs(coverDir)

	sql = '''select vid,title_id,id from {tn} where artist_id={an} and relevant=1 
			 and medley=0 and cover=0 and {cn};'''.\
		format(tn=TABLE, an=artist, cn=constraint[0])

	c.execute(sql)
	tracks = c.fetchall()

	if len(tracks) == 0:
		print("[remove] Empty master data for artist", artist)
		os.system("rm -r -f master/{}".format(artist))
		os.system("rm -r -f cover/{}".format(artist))
		continue

	allMastersTrack = set([row[1] for row in tracks])
	print("[downloadMusic] Found {} masters".format(len(allMastersTrack)))

	if len(allMastersTrack) < LEAST_MASTER_SIZE:
		print("[remove] No enough master data for artist", artist)
		os.system("rm -r -f master/{}".format(artist))
		os.system("rm -r -f cover/{}".format(artist))
		continue

	downloaded = set()

	for row in tracks:
		vid = row[0]
		title_id = row[1]
		true_id = row[2]

		if title_id not in downloaded:

			audioPath = artistDir + "/" + str(true_id) + ".mp3"
			os.system("youtube-dl --id -x --audio-format mp3 http://youtu.be/{}".format(vid))
			print("[move] mv master {}.mp3 {}".format(vid, audioPath))
			os.system("mv -- {}.mp3 {}".format(vid, audioPath))
			downloaded.add(title_id)

	for title_id in allMastersTrack:
		# download cover songs
		# go to master and find the title_id, find all cover=1 songs
		print("[downloadMusic] Start download COVER music for title_id", title_id)
		cover_sql = '''select vid,id from {tn} where title_id = {tid} and
					   relevant=1 and medley=0 and cover=1;'''.\
			format(tn=TABLE, an=artist, tid=title_id)
		c.execute(cover_sql)
		rows = c.fetchall()
		print("[downloadMusic] Found {} covers".format(len(rows)))

		for i in range(len(rows)):
			vid = rows[i][0]
			true_id = rows[i][1]
			coverPath = coverDir + "/" + str(true_id) + ".mp3"
			os.system("youtube-dl --id -x --audio-format mp3 http://youtu.be/{}".format(vid))
			print("[move] mv cover {}.mp3 {}".format(vid, coverPath))
			os.system("mv -- {}.mp3 {}".format(vid, coverPath))
			allMastersTrack.add(title_id)



	# download live songs
	# basically same algorithm as master, add check if in master
	constraint = ("soundsrc in (3,4)", "live")
	print("[downloadMusic] Start download LIVE music for", artist)

	artistDir = constraint[1] + "/" + str(artist)

	if not os.path.exists(artistDir):
		os.makedirs(artistDir)

	sql = '''select vid,title_id,id from {tn} where artist_id={an} and relevant=1 
	         and medley=0 and cover=0 and {cn};'''.\
		format(tn=TABLE, an=artist, cn=constraint[0])

	c.execute(sql)
	tracks = c.fetchall()

	print("[downloadMusic] Found {} lives".format(len(tracks)))

	for row in tracks:
		vid = row[0]
		title_id = row[1]
		true_id = row[2]
		if title_id in allMastersTrack:
			audioPath = artistDir + "/" + str(true_id) + ".mp3"
			os.system("youtube-dl --id -x --audio-format mp3 http://youtu.be/{}".format(vid))
			print("[move] mv live {}.mp3 {}".format(vid, audioPath))
			os.system("mv -- {}.mp3 {}".format(vid, audioPath))
		else:
			print("[downloadMusic] Cannot find master for live", true_id)




