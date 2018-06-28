# another try for name clustering.
# playlist names are not splitted
# only remove special characters and cluster same playlists

import pickle_utility
import app_settings
import json
import readData
import re
from nltk.stem import WordNetLemmatizer

wordDict = pickle_utility.load("wordDict_withoutIrrelevant")
#yearsDict = pickle_utility.load("yearsDict")
lookupDict = pickle_utility.load("lookupDict")
wl = WordNetLemmatizer
irrelevant = ["the", "playlist", "favorite", "favourite", "best", "top", "tracks", "mix" , "my"]
# years = []

def create_wordDict():
    words = dict()
    for k in lookupDict:
        playlist = re.split(' |_|-', k)
        name = []
        out = ""
        for j in range(len(playlist)-1):
            name.append(playlist[j])
        id = playlist[-1]
        for i in range(len(name)):
            tmp = name[i]
            tmp = re.sub("[^\w\s\_]", "", tmp)
            tmp = tmp.lower()
            if tmp not in irrelevant:
                out = out + tmp
        if out not in words:
            words[out] = [id]
        else:
            words[out].append(id)
        # if hasNumbers(out):
        #     years.append(out)
    pickle_utility.dump(words, "wordDict_withoutIrrelevant")

def create_yearDict():
    years = dict()
    for k in lookupDict:
        playlist = re.split(' ', k)
        id = playlist[-1]
        name = []
        for j in range(len(playlist) - 1):
            name.append(playlist[j])
        match = re.match(".*([1-2][0-9]{3})", str(name))
        if match is not None:
        #     year = re.split(".*([1-2][0-9]{3})", str(name))
            search = re.search('\d{4}', str(match))
            date = search.group()
            if date not in years:
                years[date] = [id]
            else:
                years[date].append(id)
    pickle_utility.dump(years, "yearsDict")

#TODO put normalisation of strings in a method

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def create_challenge_lookupDict():
    challenge_dict = dict()
    data = json.load(open(app_settings.CHALLENGE_SET))
    playlists=[]
    for playlist in data["playlists"]:
        pl=readData.extract_playlist_info(playlist)
        challenge_dict[pl[0]] = data

#TODO delete irrelevant words from input
def look_up_pl_name(playlistname):
    ids = []
    name = re.split(' ', playlistname)
    out = ""
    print(name)
    for i in range(len(name)):
        tmp = name[i]
        tmp = re.sub("[^\w\s\_]", "", tmp)
        tmp = tmp.lower()
        if tmp not in irrelevant:
            out = out + tmp
    ids.append(wordDict.get(out))
    return ids

# checks if the year is stored in yearsDict and returns the entries
def look_up_year(playlistname):
    ids = []
    name = re.split(' ', playlistname)
    out = ""
    print(name)
    for i in range(len(name)):
        tmp = name[i]
        tmp = re.sub("[^\w\s\_]", "", tmp)
        tmp = tmp.lower()
        match = re.match(".*([1-2][0-9]{3})", str(tmp))
        if match is not None:
            search = re.search('\d{4}', str(match))
            date = search.group()
    ids.append(yearsDict.get(date))
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

# returns a dict with ids of playlists of the same year if year in playlistname
def get_similar_pl_by_year(playlists):
    result_dict = dict()
    for entry in playlists:
        entry_split = entry.split('###')
        name = entry_split[0]
        id = entry_split[1]
        match = re.match(".*([1-2][0-9]{3})", str(name))
        if match is not None:
            result_dict[id] = look_up_year(name)
    return result_dict

# create_wordDict()
# create_yearDict()


# for entry in years:
#     print(str(entry))
print(get_similiar_pl_by_name(["the beach boys###123"]))
# res = open('resultDict', 'wb')
# id = "123"
# pickle.dump(tmp[id], res)
#

wd = pickle_utility.load('wordDict_withoutIrrelevant')
# # for i in wd:
# #     print(str(i))
print(len(wd))

#yd = pickle_utility.load('yearsDict', 'rb')
# for entry in yd:
#         print(entry)
# print(get_similar_pl_by_year(["newRock2015###1"]))

# rd = pickle.load(open("resultDict", "rb"))
# for i in rd:
#     print(str(i))