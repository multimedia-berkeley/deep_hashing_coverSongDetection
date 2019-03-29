import AudioTransform as at


TESTS = [
	# "live", 
	"live_clip10", 
	# "live_clip20", 
	# "live_clip30", 
	"live_clip40", 

	# "cover",
	"cover_clip10",
	# "cover_clip20",
	# "cover_clip30",
	"cover_clip40",

]

TEST_MAP = {
	
	1:"CQT_LIBROSA_NBIN96",
	2:"CQT_LIBROSA_NOLOG_NBIN96",
	3:"CQT_LIBROSA_BO24",
	4:"CQT_LIBROSA_NOLOG_BO24",


}


AUDIO_TRANS_MAP = {


	"CQT_LIBROSA_NBIN96":at.CQT_LIBROSA(nbin=96).fun,
	"CQT_LIBROSA_NOLOG_NBIN96":at.CQT_LIBROSA_NOLOG(nbin=96).fun,
	"CQT_LIBROSA_BO24":at.CQT_LIBROSA(binPerOctave=24).fun,
	"CQT_LIBROSA_NOLOG_BO24":at.CQT_LIBROSA_NOLOG(binPerOctave=24).fun,
	# "CQT_LIBROSA_NBIN72":at.CQT_LIBROSA(nbin=72).fun,

	# "CQT_LIBROSA_HOP64":at.CQT_LIBROSA(hopLength=64).fun,
	# "CQT_LIBROSA_HOP128":at.CQT_LIBROSA(hopLength=128).fun,

	# "CQT_LIBROSA_BIN12":at.CQT_LIBROSA(binPerOctave=12).fun,
	
	# "CQT_LIBROSA_DOWN4":at.CQT_LIBROSA(downsample=4).fun,
	# "CQT_LIBROSA_DOWN2":at.CQT_LIBROSA(downsample=2).fun,

	# "CQT_LIBROSA_GRP2":at.CQT_LIBROSA(groupSize=2).fun,
	# "CQT_LIBROSA_GRP3":at.CQT_LIBROSA(groupSize=3).fun,
}


HP_TRANS_MAP = {

	"PITCH_SHIFT_3":at.PITCH_SHIFT(nPitch=3).fun,
	# "PITCH_SHIFT_4":at.PITCH_SHIFT(nPitch=4).fun,
	# "PITCH_SHIFT_5":at.PITCH_SHIFT(nPitch=5).fun,
	# "PITCH_SHIFT_6":at.PITCH_SHIFT(nPitch=6).fun,
	# "PITCH_SHIFT_7":at.PITCH_SHIFT(nPitch=7).fun,

	# "TIME_STRETCH_2_0.2":at.TIME_STRETCH(maxStretch=2, interval=0.2).fun,
	# "TIME_STRETCH_2_0.5":at.TIME_STRETCH(maxStretch=2, interval=0.5).fun,
	# "TIME_STRETCH_2_1":at.TIME_STRETCH(maxStretch=2, interval=1).fun,
	# "TIME_STRETCH_3_0.2":at.TIME_STRETCH(maxStretch=3, interval=0.2).fun,
	# "TIME_STRETCH_3_0.5":at.TIME_STRETCH(maxStretch=3, interval=0.5).fun,
}


