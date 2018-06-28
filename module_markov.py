from collections import Counter
import pickle
import struct;
import readChallengeFile
import pickle_utility
import app_settings

print(struct.calcsize("P") * 8)

FILEPATH = app_settings.PICKLE_DUMP

def create_chain_file(seed_track_set, pidDict):
    outDict = dict()
    myd = pidDict
    l=len(myd.values())
    j=0
    for trackList in myd.values():
        print(j,"/",l)
        trackList = trackList.split()
        i = 0
        for track in trackList:
            if track in seed_track_set:
                # we need the next track
                if i + 1 < len(trackList):
                    nextTrack = trackList[i + 1]
                    try:
                        outDict[track].append(nextTrack)
                    except:
                        outDict[track] = [nextTrack]
            i += 1
        j+=1

    for e in seed_track_set:
        if e not in outDict.keys():
            outDict[e]=[]
    return outDict


def get_songs_from_challenges():
    seed_track_set = set()
    pls = readChallengeFile.get_challenge_playlists()
    for playlist in pls:
        songs = playlist["tracks"]
        song_ids = [str(s["track_uri"]) for s in songs]
        seed_track_set.update(song_ids)
    return seed_track_set

#playlists as dict with k,v
def enrich_playlists(playlists, nr_new_tracks_per_track):
    # playlists=playlists.values()
    file = open(FILEPATH+"count_chain_file_dict", "rb")
    dic = pickle.load(file)
    outPl = []
    outDict=dict()
    for k,pl in playlists.items():
        trackSet = set(pl)
        tempList = []
        tempList.extend(pl)
        for track in pl:
            onlyTracks = [e[0] for e in dic[track].most_common(nr_new_tracks_per_track) if e[0] not in trackSet]
            tempList.extend(onlyTracks)
        outPl.append(tempList)
        outDict[k]=tempList

    pickle_utility.dump(outDict, "MarkovOut")
    return outDict


def init_pickle_files():
    f = open(FILEPATH+"pidtotracks", "rb")
    pidDict = pickle.load(f)
    sts = get_songs_from_challenges()

    d = create_chain_file(sts, pidDict)
    pidDict=None
    file = open(FILEPATH+"chain_file_dict", "wb")
    pickle.dump(d, file)

    file = open(FILEPATH+"chain_file_dict", "rb")
    dic = pickle.load(file)
    for k, v in dic.items():
        cnt = Counter(v)
        cnt.most_common()
        dic[k] = cnt

    file = open(FILEPATH+"count_chain_file_dict", "wb")
    pickle.dump(dic, file)

#   when first starting this
# init_pickle_files()

# sts = get_songs_from_challenges()
# print("spotify:track:3rZ4i6DtuqyqSh0aayhlmq" in sts)

# file = open("D:/_LUD/franziFiles/count_chain_file_dict", "rb")
# dic = pickle.load(file)
# #spotify:track:3rZ4i6DtuqyqSh0aayhlmq
# print(dic["spotify:track:3rZ4i6DtuqyqSh0aayhlmq"])
# onlyTracks = [e[0] for e in dic["spotify:track:3rZ4i6DtuqyqSh0aayhlmq"].most_common(3)]
# print(onlyTracks)
# for e in dic["spotify:track:3rZ4i6DtuqyqSh0aayhlmq"]:
#     print(e[0])

#3rZ4i6DtuqyqSh0aayhlmq