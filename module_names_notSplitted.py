# another try for name clustering.
# playlist names are not splitted
# only remove special characters and cluster same playlists

import app_settings
import pickle_utility
import json
import readData
import re
from nltk.stem import WordNetLemmatizer

wordDict = pickle_utility.load("wordDict_namesNotSplitted")
lookupDict = pickle_utility.load("lookupDict")
wl = WordNetLemmatizer


def create_wordDict():
    words = dict()
    for k in lookupDict:
        playlist = k.split(" ")
        name = []
        out = ""
        for j in range(len(playlist)-1):
            name.append(playlist[j])
        id = playlist[-1]
        for i in range(len(name)):
            tmp = name[i]
            tmp = re.sub("[^\w\s\_]", "", tmp)
            tmp = tmp.lower()
            out = out + tmp
        if out not in words:
            words[out] = [id]
        else:
            words[out].append(id)
    pickle_utility.dump(words,"wordDict_NamesNotSplitted")


def create_challenge_lookupDict():
    challenge_dict = dict()
    data = json.load(open(app_settings.CHALLENGE_SET))
    playlists=[]
    for playlist in data["playlists"]:
        pl=readData.extract_playlist_info(playlist)
        challenge_dict[pl[0]] = data

def look_up_pl_name(playlistname):
    ids = []
    name = re.split(' ', playlistname)
    out = ""
    #print(name)
    for i in range(len(name)):
        tmp = name[i]
        tmp = re.sub("[^\w\s\_]", "", tmp)
        tmp = tmp.lower()
        out = out + tmp
    ids.append(wordDict.get(out))
    return ids

# input is playlist name + id
# use the name for finding similiar playlists
# returns a dict with id of playlist as key and similar playlists as value
def get_similiar_pl_by_name(playlists):
    result_dict = dict()
    for entry in playlists:
        entry_split = entry.split('###')
        name = entry_split[0]
        id = entry_split[1]
        result_dict[id] = look_up_pl_name(name)
        # result_file = open('resultDict', 'wb')
        # pickle.dump(result_dict[id], result_file)
    return result_dict