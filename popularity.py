import module_cluster
import createTrackDict
import app_settings
import pickle_utility
from collections import defaultdict, Counter
import concurrent.futures
from multiprocessing import Pool, Value

def main():
    test_predict()

def test_predict():
    pids, challenge_data = createTrackDict.process_mpd(app_settings.CHALLENGE_SET, 1)

    challenge_dict = {}
    for pid, track in zip(pids, challenge_data):
        challenge_dict[pid] = track.split()

    predictions = module_cluster.predit_doc2vec_similar_pids(challenge_dict, 75)
    popularity(predictions)

def popularity(data, pidtotracks = None, name = "DefaultName"):
    if(pickle_utility.exists_file(name)):
        return pickle_utility.load(name)
    if(pidtotracks == None):
        pidtotracks = pickle_utility.load("pidtotracks")

    occurences = pickle_utility.load("trackOccurences")

    pop_dict = {}
    counter = 0

    print("Start popularity ranking...")
    for key, pid_predictions in data.items():
        track_pop_dict = Counter()
        for pid in pid_predictions:
            tracks = pidtotracks[int(pid)]
            for track in tracks.split():
                track_pop_dict[track] = occurences[track]
        pop_dict[key] = [i[0] for i in track_pop_dict.most_common(1000)]
        counter += 1
        if(counter % 100 == 0):
            print("Processed {} playlists".format(counter))

    pickle_utility.dump(pop_dict ,name)
    return pop_dict


def popularity_cluster(data, caching = True):
    predictions = data.items()
    
    pidtotracks = pickle_utility.load("pidtotracks")

    occurences = pickle_utility.load("trackOccurences")

    popularity_dict = defaultdict(int)

    #p = Pool()
    counter = 0
    addProcesses = []
    pidProcesses = []

    caching_predictions = {}
    unique_tracks = set()

    mapping_dict = {}

    for key, prediction in predictions:
        prediction_set = set()
        mapping_dict[key] = prediction[0]
        for pid in prediction:
            tracks = pidtotracks[pid]
            prediction_set.add(tracks)
            

    print("Number of cached strings: {0}".format(len(caching_predictions.values())))
    processed_track_strings = set()
    for key, prediction in caching_predictions.items():
        track_set = set()
        for track_string in prediction:
            if(not track_string in processed_track_strings):
                for track in track_string.split():
                    track_set.add(track)
                processed_track_strings.add(track_string)
            else:
                print("Caching worked")
        caching_predictions[key] = track_set

    return popularity_dict

def process_pids(pids, pidtotracks):
    tracks = pidtotracks[pid].split()
    print(tracks)

def process_tracks(tracks, pid):
    popularity_dict = defaultdict(int)
    for track in tracks:
        popularity_dict[track] += 1

    return popularity_dict, pid



if __name__ == '__main__':
    main()