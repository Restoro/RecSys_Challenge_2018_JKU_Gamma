import glob
#overall
MPD_PATH = "E:/LUGD/mpd.v1/mpd/"
CHALLENGE_PATH = "E:/LUGD/challenge/"
PICKLE_DUMP = "E:/LUGD/Pickle Dumps/"

CHALLENGE_SET = CHALLENGE_PATH + "challenge_set.json"
MPD_SET = MPD_PATH + "mpd.slice.*.json"

MPD_FILENAMES = glob.glob(MPD_SET)

#cluster settings
VECSIZE = 300
WINDOW = 2
SELECTION = 10

#print submission
NR_OF_TRACKS = 500
OUTPUT_PATH = CHALLENGE_PATH
OUTPUT_FILE = "Gamma_Submission.csv"
TEAM_NAME = "JKU_Gamma"
EMAIL = "x@students.jku.at"
