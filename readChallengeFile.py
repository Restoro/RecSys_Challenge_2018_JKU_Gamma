import json
from collections import Counter

import time
from gensim.models import Doc2Vec

import readData
import app_settings
# read


#start with 0
def get_challenge_data(challenge_nr):
    # challenge one 1000 lists only name given
    data = json.load(open(app_settings.CHALLENGE_SET))
    playlists = data["playlists"]
    challenge = playlists[1000*challenge_nr:1000*challenge_nr+1000]
    # print(challenge[0])
    # print(challenge[-1])
    return challenge

def check_distances(list,model):
    for e in list:
        for tag in model.docvecs.doctags.items():
            dist = editdistance.eval(e, tag[0])

            if (dist < 2):
                print(dist)
                print(e)
                print(tag[0])
                print(model.docvecs.most_similar(positive=[tag[0]], negative=[], topn=10))

#challenge 0

def challenge0():
    playlists=get_challenge_data(0)

    #get all names:
    name_list=[entry["name"] for entry in playlists]
    name_set=set(name_list)
    print(len(name_set))
    print(name_list[0])
    # model=readData.trainModel()
    # model.save("savedModelFull2323")
    model = Doc2Vec.load("savedModelFull")
    no_matches=[]
    for name in name_list[:100]:
        print("############")
        print(name)
        match=False
        for tag in model.docvecs.doctags.items():
            dist=editdistance.eval(name, tag[0])

            if(dist<1):
                print(dist)
                print(tag[0])
                print(model.docvecs.most_similar(positive=[name], negative=[], topn=10))
                match=True
        if match==False:
            print("+++++++++++++++")
            print("no match for ",name)
            print("+++++++++++++++")
            no_matches.append(name)

    print("no matches for")
    print(no_matches)

    check_distances(no_matches,model)


# import readData
# playlists=get_challenge_data(0)
#
# #get all names:
# name_list=[entry["name"] for entry in playlists]
# name_set=set(name_list)
# for na in name_set:
#     print(na)
# for n in name_set:
#
#     i=readData.search_playlist_name(n)
#     if i==0:
#         print(n)
# # challenge0()

#title and one song
# def challenge1():

def statistics_challenge0():
    # we search only by name
    # check if name found and report all lists under 10 equal lists in mpd data set
    playlists=[]
    for i in range(10):
        playlists.extend(get_challenge_data(i))
    for e in playlists:
        try:
            s=e["name"]
        except:
            print(e)
    name_list = [entry["name"] for entry in playlists]
    name_set = set(name_list)
    print("uniqe PL-names in challenges : ",len(name_set))

    #unefficient
    # zero_matches=[]
    # for name in name_set:
    #     results=readData.search_playlist_name(name)
    #     if results<10:
    #         print("only "+str(results)+" matches for ",name)
    #         if results==0:
    #             zero_matches.append(name)
    # print(zero_matches)

    # more efficient

    res=readData.search_playlist_names(name_set)
    for l in res:
        if l[1]==0:
            print(l)



import compare
def compute_similarities(onlyTracks,playlist):
    # find pls with no name attribute:

    #get tracks
    tracks=[e["track_uri"] for e in onlyTracks["tracks"]]
    same_length_equality, unequal_length_equality=compare.compare_tracks_to_playlist(tracks,playlist)
    if same_length_equality==1 and unequal_length_equality>0.2:
        print(unequal_length_equality)
        print(print("lol"))

def get_no_name_pls(no_names):
    #open all files and compare with no names
    playlist_gen=readData.get_file_contents(1000)
    start=time.clock()
    for playlists in playlist_gen:
        i = 0
        for playlist in no_names:
            # print("compared ",i)
            i+=1
            for pl in playlists:
                compute_similarities(playlist,pl)
        print("comparing one file took (minutes) ",str(time.clock()-start))

# input: name , songs (optional)

def get_challenge_playlists():
    playlists = []
    playlists.extend(get_challenge_data(0))
    playlists.extend(get_challenge_data(9))

    for i in range(8):
        playlists.extend(get_challenge_data(i + 1))

    return playlists

def gen_best_playlists():
    #get all pls with name
    playlists = []
    playlists.extend(get_challenge_data(0))
    playlists.extend(get_challenge_data(9))

    for i in range(8):

        playlists.extend(get_challenge_data(i+1))
    no_names=[]
    names=[]
    for e in playlists:
        try:
            s = e["name"]
            names.append(e)
        except:
            # print(e)
            no_names.append(e)


    print(len(no_names))


    # get_no_name_pls(no_names)
    # get cluster stuff


    name_list = [entry["name"] for entry in names]
    name_set = set(name_list)
    print("uniqe PL-names in challenges : ", len(name_set))

    res = readData.search_playlist_names(name_set,False)
    for l in res:
        if l[1] == 0:
            print(l)
    #get 500 top songs from this cluster



# gen_best_playlists()
# statistics_challenge0()
