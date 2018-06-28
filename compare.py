# read
from os import listdir
from os.path import isfile, join
import time
import app_settings

onlyfiles = app_settings.MPD_FILENAMES

# tuple(pl_name,tuple(list(pl_track_names),list(pl_track_ids))
import json


def extract_playlist_info(playlist):
    name = playlist["name"]
    songs = playlist["tracks"]
    song_ids = [str(s["track_uri"]) for s in songs]
    song_names = [str(s["track_name"]) for s in songs]
    # song_ids = " ".join(song_ids)
    # tokenized_text = word_tokenize(song_ids)
    return (name, (song_names, song_ids))


def compare_playlist_equality(pl1, pl2):
    shortest = min(len(pl1[1][1]), len(pl2[1][1]))
    longest = max(len(pl1[1][1]), len(pl2[1][1]))
    songs1 = pl1[1][1]
    songs2 = set(pl2[1][1])

    found = 0.0
    ctr = 0
    for song in songs1:

        if song in songs2:
            found += 1
        ctr += 1
    esim = found / shortest
    uesim = found / longest
    if esim > 0.1:
        print(pl1[0] + "  --VS--  ", pl2[0])
        print("nr of tracks ", len(pl1[1][1]), " --- ", len(pl2[1][1]))
        print("equal length comparison: ")
        print(esim)
        print("unequal length comparison: ")
        print(uesim)
        print("same songs ", len(set(songs1).intersection(songs2)))
    return esim,uesim


def find_playlist(id, files, PATH):
    files.sort()
    if len(files) != 1000:
        print("wrong file amount")
        exit(1)
    # print(files[:3])
    numbers = [f[10:-5] for f in files]
    ranges = [(str(n).split("-")) for n in numbers]
    # print(ranges[:4])
    ctr = 0
    for range in ranges:
        if int(id) >= int(range[0]) and int(id) <= int(range[1]):
            break
        ctr += 1
    correct_file = files[ctr]
    # print(correct_file)
    start = time.clock()
    data = json.load(open(PATH + correct_file))
    # print("open file ",time.clock()-start)
    playlists = []
    for playlist in data["playlists"]:
        if playlist["pid"] == id:
            # print("found")
            return playlist


# cmp playlist ids
def compare_pids(id1, id2):
    start = time.clock()
    id1=int(id1)
    id2=int(id2)
    p1 = find_playlist(id1, onlyfiles, PATH)
    p2 = find_playlist(id2, onlyfiles, PATH)
    # print("finding playlists ", time.clock() - start)
    start = time.clock()
    p1 = extract_playlist_info(p1)
    p2 = extract_playlist_info(p2)
    # print("extracting playlists ",time.clock() - start)
    start = time.clock()

    return compare_playlist_equality(p1, p2)
    # print("comparing playlists ",time.clock() - start)


def compare_tracks_to_playlist(tracks, playlist):
    track_ids = extract_playlist_info(playlist)[1][1]
    shorter = min(len(track_ids), len(tracks))
    longer = max(len(track_ids),len(tracks))
    list1Set = set(track_ids)
    list2Set = set(tracks)
    equalTracks = len(list1Set.intersection(list2Set))
    same_length_equality = equalTracks / shorter
    unequal_length_equality = equalTracks / longer
    return same_length_equality, unequal_length_equality

def compare_stringlists(sl1,sl2):
    s1=set(sl1)
    s2=set(sl2)
    equal=s1.intersection(s2).__len__()
    maxL=max(len(sl1),len(sl2))
    equalRatio=equal/maxL
    return equalRatio

#
# for i in range(3, 10000):
#     start = time.clock()
#     compare_pids(3, i)
    # print(time.clock()-start)

def plIds_with_tracks_dict():
    plTrackIdDict=dict()
    for id in range(1000000):
        print(id)
        pl=find_playlist(id,onlyfiles,PATH)
        pl=extract_playlist_info(pl)
        plTrackIdDict[id]=pl[1][1]

    if len(plTrackIdDict.keys())!=1000000:
        print("danger!! only ")
        print(len(plTrackIdDict.keys()))
    import pickle
    file=open("plTrackIdDict","wb")
    pickle.dump(plTrackIdDict,file)



# plIds_with_tracks_dict()