import json
import pickle
import collections
import operator
from builtins import print

import module_names_notSplitted
import print_submission
import module_markov
# import module_markov_500
import module_cluster
import copy
import itertools
from collections import Counter
import app_settings
import pickle_utility

# read
data = json.load(open(app_settings.CHALLENGE_SET))
playlists = data["playlists"]
originalTracks = dict()

# use pidtotracks for selecting actual tracks that should be in the submit file
print("Reading pidtotracks")
pid_dict = pickle_utility.load("pidtotracks")


def getPopularityRankedPlaylists(playlists):
    print("Reading trackOccurences")
    trackOccCount = pickle_utility.load("trackOccurences")

    rankedSimilarTrackDict = dict()
    pidToPopDict = dict()
    count = 0
    for pid, similarPids in playlists.items():
        count += 1
        print(count)
        # count popularity of similar playlists for this pid
        for similarPid in similarPids:
            popularityCounter = 0
            tracks = pid_dict[int(float(similarPid))].split(" ")
            # print(len(tracks))
            for track in tracks:
                popularityCounter += trackOccCount[track]
            pidToPopDict[similarPid] = popularityCounter

        # rearrange the similar playlists for this pid so that the most popular are at the beginning
        sortedSimilarPlaylists = dict(sorted(pidToPopDict.items(), key=operator.itemgetter(1), reverse=True))
        # for k, v in sortedSimilarPlaylists.items():
        #    print(k, v)
        rankedSimilarTrackDict[pid] = list(sortedSimilarPlaylists.keys())
        pidToPopDict.clear()
        # for k, v in rankedSimilarTrackDict.items():
        #    print(k, v)
        if count == 100:
            break
    return rankedSimilarTrackDict


# start with 0
def get_challenge_data(challenge_nr):
    # challenge one 1000 lists only name given

    challenge = playlists[1000 * challenge_nr:1000 * challenge_nr + 1000]
    # print(challenge[0])
    # print(challenge[-1])
    return challenge


def readChallengeFileAndCallOthers():
    # get all pls with name
    playlists = []
    playlists.extend(get_challenge_data(0))
    playlists.extend(get_challenge_data(9))

    for i in range(8):
        playlists.extend(get_challenge_data(i + 1))

    # list of all strings containing playlist name and playlist id of challenge set
    names_gudrun = []
    # dict with pid as key, and its track_uris in a list as value
    playlists_max = dict()
    for p in playlists:
        pTracks = []
        pID = p["pid"]
        try:
            pName = p["name"]
            # format: pName###pID
            names_gudrun.append(str(pName) + "###" + str(pID))
        except:
            # no name, only tracks -> challenge 4 or 6
            # do not call gudrun
            pass

        tracks = p["tracks"]
        for track in tracks:
            pTracks.append(track["track_uri"])
        playlists_max[pID] = pTracks

    global originalTracks
    originalTracks = copy.deepcopy(playlists_max)

	############################ MAX ################################
    print("...getting data from module_markov...")
    # important: call max first, otherwise we need to filter out the original challenge tracks
    # returns dict of pid (challengeset) and values: list of tracks
    # If I give 100, 300 get back (100 original + 2 per track)
    similarTrackDict = module_markov.enrich_playlists(playlists_max, 3)  # cannot be ensured that I actually get 3, count to make sure!

    ##enrichedTrackDict = pickle_utility.load("enriched500Pls")

	############################ PATRICK ################################
    ##print("...getting data from fullpipeline...")
    # returns dict of pid (challengeset) and values: playlist ids (from common dataset)
    # I get for every pid differently sized lists of playlist ids
    # fullpipeline main callen mit 10 (2.zeile in main) damit ich eine pipeline bekomme
    similarTrackDict = module_cluster.predit_doc2vec_similar_pids(similarTrackDict, 50)  
    ##similarTrackDict = module_cluster.predit_doc2vec_similar_pids(similarTrackDict)
    #similarTrackDict = module_cluster.predit_doc2vec_similar_tracks(similarTrackDict)


    '''
    print("...ranking by popularity...")
    rankedSimilarTrackDict = getPopularityRankedPlaylists(similarTrackDict)
    pickle_utility.dump(rankedSimilarTrackDict, "rankedPlaylists")
    return
    '''

	############################ GUDRUN ################################
    # returns dict of playlist ids with pid as key, and as value a list of playlists-lists (i.e. their id) with similar names (one list for each word in the name)
    print("...getting data from module_names...")
    returnDict = module_names_notSplitted.get_similiar_pl_by_name(names_gudrun)
    # put all pid-sub-lists into one pid-list
    similarNameDict = dict()
    for pid, pidlist in returnDict.items():
        if pidlist is not None:
            try:
                similarNameDict[pid] = []  # TODO careful, value could be empty, remember this for later
                for list in pidlist:
                    if list is not None:
                        similarNameDict[pid].extend(list)
            except:
                print("oh no ", pid, " and ", pidlist)

    print("...collecing tracks...")
    # for every challenge, collect 500 tracks
    submitArray = []


	############################ CREATE SUBMISSION FILE WITH PIDs ################################
    print("Starting with challenge 1-3")
    currentDict = dict(itertools.islice(similarNameDict.items(), 0, 3000))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 0, 3000))
    getTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    print("Starting with challenge 4")
    currentDict = dict(itertools.islice(similarTrackDict.items(), 3000, 4000))
    getTracks(pid_dict, currentDict, currentDict, submitArray)
    print("Starting with challenge 5")
    currentDict = dict(itertools.islice(similarNameDict.items(), 3000, 4000))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 4000, 5000))
    getTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    print("Starting with challenge 6")
    currentDict = dict(itertools.islice(similarTrackDict.items(), 5000, 6000))
    getTracks(pid_dict, currentDict, currentDict, submitArray)
    '''
	#challenges 7-10 from gudrun
    print("Starting with rest of challenges")
    currentDict = dict(itertools.islice(similarNameDict.items(), 4000, None))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 6000, None))
    getTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    '''
	#gudrun 7&8, patrick 9&10
    print("Starting with challenge 7&8")
    currentDict = dict(itertools.islice(similarNameDict.items(), 4000, 6000))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 6000, 8000))
    getTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    print("Starting with challenge 9&10") # None instead of end
    currentDict = dict(itertools.islice(similarTrackDict.items(), 8000, None))
    getTracks(pid_dict, currentDict, currentDict, submitArray)


	############################ CREATE SUBMISSION FILE WITH TRACKS ################################
    '''
    #patrick sends tracks
    print("Starting with challenge 1-3")
    currentDict = dict(itertools.islice(similarNameDict.items(), 0, 3000))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 0, 3000))
    getTracksfromPIDAndTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    print("Starting with challenge 4")
    currentDict = dict(itertools.islice(similarTrackDict.items(), 3000, 4000))
    getTracksfromTracks(pid_dict, currentDict, currentDict, submitArray)
    print("Starting with challenge 5")
    currentDict = dict(itertools.islice(similarNameDict.items(), 3000, 4000))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 4000, 5000))
    getTracksfromPIDAndTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    print("Starting with challenge 6")
    currentDict = dict(itertools.islice(similarTrackDict.items(), 5000, 6000))
    getTracksfromTracks(pid_dict, currentDict, currentDict, submitArray)
    print("Starting with challenge 7&8")
    currentDict = dict(itertools.islice(similarNameDict.items(), 4000, 6000))
    compensatoryDict = dict(itertools.islice(similarTrackDict.items(), 6000, 8000))
    getTracksfromPIDAndTracks(pid_dict, currentDict, compensatoryDict, submitArray)
    print("Starting with challenge 9&10") # None instead of end
    currentDict = dict(itertools.islice(similarTrackDict.items(), 8000, None))
    getTracksfromTracks(pid_dict, currentDict, currentDict, submitArray)
    '''

    '''
    for idAndTrack in submitArray:
    currentPID = idAndTrack[0]
    if len(enrichedTrackDict[int(float(currentPID))]) != 0:
        submitArray.remove(idAndTrack)
        trackArray = []
        trackArray.append(currentPID)
        trackArray.extend(enrichedTrackDict[int(float(currentPID))])
        submitArray.append(trackArray)
    '''

    # something = [id1,t1,t2,..][id2,t1,t2,..][...]
    # [currentPID, track1, track2,..][currentPID...]
    print(len(submitArray))
    print_submission.write_file(submitArray)


# use for Gudrun if patrick/max gives tracks
def getTracksfromPIDAndTracks(pid_dict, currentDict, compensatoryDict, submitArray):
    NR_OF_TRACKS = 500
    count = 0
    stopCollecting = False

    for currentPID, similarPIDs in currentDict.items():  # similarTrackDict
        # print("_",currentPID)
        trackArray = []
        trackArray.append(currentPID)
        if len(similarPIDs) == 0:
            # use predictDict instead
            tracks = compensatoryDict[int(float(currentPID))]
            for track in tracks:
                if not trackArray.__contains__(track) and not originalTracks[int(float(currentPID))].__contains__(
                        track):
                    trackArray.append(track)
                    count += 1
                    if (count == NR_OF_TRACKS):
                        submitArray.append(trackArray)
                        stopCollecting = True
                        break
        for similarPID in similarPIDs:
            if stopCollecting: break
            # print(" similar ID: ", similarPID, " ", pid_dict[int(float(similarPID))])
            tracks = pid_dict[int(float(similarPID))].split(" ")
            if len(tracks) == 0:
                # TODO does not occur, would only occur if in the dataset we would have an empty playlist, maybe use predictDict instead just in case...
                print("*******************************")
            for track in tracks:
                if not trackArray.__contains__(track) and not originalTracks[int(float(currentPID))].__contains__(
                        track):
                    trackArray.append(track)
                    count += 1
                    if (count == NR_OF_TRACKS):
                        submitArray.append(trackArray)
                        stopCollecting = True
                        break

        # in case less than 500 tracks have been found, use compensatory dict
        tracks = compensatoryDict[int(float(currentPID))]
        for track in tracks:
            if stopCollecting: break
            if not trackArray.__contains__(track) and not originalTracks[int(float(currentPID))].__contains__(
                    track):
                trackArray.append(track)
                count += 1
                if (count == NR_OF_TRACKS):
                    submitArray.append(trackArray)
                    stopCollecting = True
                    break

        if count != NR_OF_TRACKS:
            print("We have a problem...", count)
        stopCollecting = False
        count = 0


# use for patrick/max if they give tracks
def getTracksfromTracks(pid_dict, currentDict, compensatoryDict, submitArray):
    NR_OF_TRACKS = 500
    count = 0

    for currentPID, tracks in currentDict.items():  # similarTrackDict
        # print("_",currentPID)
        trackArray = []
        trackArray.append(currentPID)
        if len(tracks) == 0:
            print("We have a problem")
        for track in tracks:
            if not trackArray.__contains__(track) and not originalTracks[int(float(currentPID))].__contains__(track):
                trackArray.append(track)
                count += 1
                if (count == NR_OF_TRACKS):
                    submitArray.append(trackArray)
                    break

        if count != NR_OF_TRACKS:
            print("We have a problem...", count)
        count = 0


# use for all if patrick/max gives pids
# TODO next: add popularity vote
def getTracks(pid_dict, currentDict, compensatoryDict, submitArray):
    NR_OF_TRACKS = 500
    count = 0
    stopCollecting = False

    for currentPID, similarPIDs in currentDict.items():  # similarTrackDict
        # print("_",currentPID)
        trackArray = []
        trackArray.append(currentPID)
        if len(similarPIDs) == 0:
            # use predictDict instead
            similarPIDs = compensatoryDict[int(float(currentPID))]
        for similarPID in similarPIDs:
            if stopCollecting: break
            # print(" similar ID: ", similarPID, " ", pid_dict[int(float(similarPID))])
            tracks = pid_dict[int(float(similarPID))].split(" ")
            if len(tracks) == 0:
                # TODO does not occur, would only occur if in the dataset we would have an empty playlist, maybe use predictDict instead just in case...
                print("*******************************")
            for track in tracks:
                if not trackArray.__contains__(track) and not originalTracks[int(float(currentPID))].__contains__(
                        track):
                    trackArray.append(track)
                    count += 1
                    if (count == NR_OF_TRACKS):
                        submitArray.append(trackArray)
                        stopCollecting = True
                        break

        # in case less than 500 tracks have been found, use compensatory dict
        similarPIDs = compensatoryDict[int(float(currentPID))]
        for similarPID in similarPIDs:
            if stopCollecting: break  # breaks if previous loop gathered enough tracks
            # print(" similar ID: ", similarPID, " ", pid_dict[int(float(similarPID))])
            tracks = pid_dict[int(float(similarPID))].split(" ")
            if len(tracks) == 0:
                # TODO does not occur, would only occur if in the dataset we would have an empty playlist, maybe use predictDict instead just in case...
                print("*******************************")
            for track in tracks:
                if not trackArray.__contains__(track) and not originalTracks[int(float(currentPID))].__contains__(
                        track):
                    trackArray.append(track)
                    count += 1
                    if (count == NR_OF_TRACKS):
                        submitArray.append(trackArray)
                        stopCollecting = True
                        break

        if count != NR_OF_TRACKS:
            print("We have a problem...", count)
        stopCollecting = False
        count = 0


def readGudrunsFile():
    pid_dict = pickle_utility.open("resultDictPickleDump")
    print((pid_dict))


# readChallengeFileAndCallOthers()
# readGudrunsFile()

'''
Fürs getten vom challenge file sowie das predicten    
pids, challenge_data = createTrackDict.process_mpd("challenge/challenge_set.json", 1) #1st parameter regex (e.g."D:/_LUD/mpd.v1/mpd/data/mpd.slice.*.json"), 2nd parameter nr of files

    challenge_dict = {}
    for pid, track in zip(pids, challenge_data):
        challenge_dict[pid] = track

    predictions = predict(challenge_dict)
'''

# fullpipeline main nur kurz callen (bis das dict erstellt ist und schaun ob ich es dann öffnen kann
# fullPipeline.main()

# file = open("pidtotracks", "rb")
# pid_dict = pickle.load(file)
# print(pid_dict[214610])
# tracks = pid_dict[0].split(" ")
# for track in tracks:
# print(track)


readChallengeFileAndCallOthers();
