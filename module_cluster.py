from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

from sklearn.decomposition import TruncatedSVD, PCA

from itertools import compress
from collections import Counter, defaultdict
import numpy as np
import readData
import pickle_utility
import glob
import json
import os
import createTrackDict
import readChallengeFile

import app_settings

def main():
    #generate_doc2vec_files(app_settings.MPD_FILENAMES)
    fit_doc2vec_pca()
    test_predit()


def predit_doc2vec_similar_tracks(data, requested_tracks):
    if(not pickle_utility.exists_file("doc2vec_similiar_tracks_dict_{0}N".format(requested_tracks))):
        print("Load Doc2Vec...")

        model = pickle_utility.load("fullModeD2V" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")
        print("Predict...")
        count = 0

        result_dict = {}

        for key, value in data.items():
            iv = model.infer_vector(value)
            sim = model.wv.most_similar([iv],topn=requested_tracks)
            tracks = [sim[i][0] for i in range(requested_tracks)]
            result_dict[key] = tracks
            count += 1
            print("Proccessed {0} Playlists".format(count))

        print("Dump...")
        pickle_utility.dump(result_dict, "doc2vec_similiar_tracks_dict_{0}N".format(requested_tracks))
    else:
        print("Load Pickle for Pred...")
        result_dict = pickle_utility.load("doc2vec_similiar_tracks_dict_{0}N".format(requested_tracks))

    return result_dict

def predit_doc2vec_similar_pids(data, requested_pids):
    if(not pickle_utility.exists_file("doc2vec_similiar_pids_dict_{0}N".format(requested_pids))):
        print("Load Doc2Vec...")
        model = pickle_utility.load("fullModeD2V" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")
        
        print("Predict...")
        count = 0

        result_dict = {}

        for key, value in data.items():
            iv = model.infer_vector(value)
            sim = model.docvecs.most_similar([iv],topn=requested_pids)
            splits = [sim[i][0].split()[-1] for i in range(requested_pids)]
            pds = [x for x in splits if x.isdigit()]
            result_dict[key] = pds
            count += 1
            print("Proccessed {0} Playlists".format(count))

        print("Dump...")
        pickle_utility.dump(result_dict, "doc2vec_similiar_pids_dict_{0}N".format(requested_pids))
    else:
        print("Load Pickle for Pred...")
        result_dict = pickle_utility.load("doc2vec_similiar_pids_dict_{0}N".format(requested_pids))

    return result_dict

def predit_doc2vec_pca(data):
    print("Load Doc2Vec...")
    kmeans = pickle_utility.load("fullModeD2VCluster" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")

    print(len(data))

    ivs = []
    model = pickle_utility.load("fullModeD2V" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")
    for key, value in data.items():
        iv = model.infer_vector(value)
        ivs.append(iv)
    
    X=ivs

    pca = pickle_utility.load("fullModeD2VPCA" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")
    pca_result = pca.transform(X)

    print("Predict...")
    preds = kmeans.predict(pca_result)

    split =  model.docvecs.index2entity[0].split()[-1]

    pds = [model.docvecs.index2entity[i].split()[-1] for i in range(len(model.docvecs.index2entity))]
    #pds = [x for x in splits if x.isdigit()]
    
    return generate_data_from_cluster_center_d2v(data, kmeans, pds, preds)

def predit_count_vec(data):
    pipeline = pickle_utility.load("pipeline")

    mystrings = []
    for value in data.values():
        mystrings.append(" ".join(value))

    print("Predict...")
    predictions = pipeline.predict(mystrings)

    pids = pickle_utility.load("pids")

    pids = np.array(pids)
    caching = {}

    for i, (key, value) in enumerate(data.items()):
        pred = predictions[i]
        if pred in caching:
            data[key] = caching[pred]
        else:
            cluster_ids = get_all_from_center_c(pids, pipeline.named_steps['kmeans'].labels_ ,pred)
            caching[pred] = cluster_ids
            data[key] = (cluster_ids)

    return data

def generate_data_from_cluster_center_d2v(data, kmeans, docvecs, predictions):
    pids = np.array(docvecs)
    caching = {}

    for i, (key, value) in enumerate(data.items()):
        pred = predictions[i]
        if pred in caching:
            data[key] = caching[pred]
        else:
            cluster_ids = get_all_from_center_c(pids, kmeans.labels_ ,pred)
            digit_cluster_ids = [x for x in cluster_ids if x.isdigit()]
            caching[pred] = digit_cluster_ids
            data[key] = (digit_cluster_ids)


    return data

def cluster_indices_numpy(clustNum, labels_array):  # numpy
    return np.where(labels_array == clustNum)[0]

def get_all_from_center_c(docvec, labels, cluster_center):
    indices = cluster_indices_numpy(cluster_center, labels)
    selected = docvec[indices]
    return selected

def fit_doc2vec_pca():

    model=pickle_utility.load("fullModeD2V" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")

    X=model.docvecs.doctag_syn0
    print(X.shape)
    print("PCA...")

    pca = PCA(n_components=77)
    pca_result = pca.fit_transform(X)
    print("Dump PCA")
    pickle_utility.dump(pca, "fullModeD2VPCA" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")

    print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))
    print('Explained variation sum: {}'.format(pca.explained_variance_ratio_.sum()))

    print("Fit clusters")
    kmeans = MiniBatchKMeans(n_clusters=50).fit(pca_result)
    print("Dump clusters")

    pickle_utility.dump(kmeans, "fullModeD2VCluster" + str(app_settings.VECSIZE) + "D" + str(app_settings.WINDOW) + "W")

def fit_count_vec():
    pipeline = Pipeline([('count', CountVectorizer()),('svd', TruncatedSVD()),('kmeans', MiniBatchKMeans())])

    pipeline.set_params(count__token_pattern=r"(?u)\b\w+:\w+:\w+\b", svd__n_components=100, kmeans__n_clusters=50 )

    print("Start fitting...")
    pipeline.fit(data)

    print(pipeline.named_steps['svd'].explained_variance_ratio_)
    print(pipeline.named_steps['svd'].explained_variance_ratio_.sum())

    print("Dump pipeline...")
    pickle_utility.dump(pipeline, "pipeline")

def get_tagged_docs(files):
    class tagged_docs:
        def __iter__(self):
            for f in files:
                print(f)
                #fullPath = app_settings.MPD_PATH + str(f)
                data = json.load(open(f))
                for playlist in data["playlists"]:
                    name = playlist["name"]
                    # name+="-"+str(playlist["pid"])+" "+name
                    name=[name+" "+str(playlist["pid"]),name]
                    songs = playlist["tracks"]
                    song_ids = [str(s["track_uri"]) for s in songs]
                    # song_ids = " ".join(song_ids)
                    # tokenized_text = word_tokenize(song_ids)
                    doc = TaggedDocument( song_ids,name)
                    
                    yield doc
    return tagged_docs()

def generate_doc2vec_files(files):
    #docs = createTrackDict.generate_tagged_docs(files)
    docs = get_tagged_docs(files)
    model=Doc2Vec(vector_size=app_settings.VECSIZE, window=app_settings.WINDOW,workers=8)
    model.build_vocab(docs)
    pickle_utility.dump(model,"vocabModel")
    print(model.iter)
    model.train(docs, total_examples=model.corpus_count, epochs=model.iter)

    pickle_utility.dump(model, "fullModeD2V"+str(app_settings.VECSIZE)+"D"+str(app_settings.WINDOW)+"W")

    return model

def generate_count_vec_files():
    if(not pickle_utility.exists_file("pidtotracks")):
        createTrackDict.create_pid_dict(50) #use 10 instead of 1000 so that it doesn't run forever^^
        print("******************************************")

    print("Load tracks and pids")
    data = pickle_utility.load("pidtotracks")

    tracks = data.values()
    pids = data.keys()

    print("Dump pids")
    if(not pickle_utility.exists_file("pids")):
        pickle_utility.dump(list(pids), "pids")

    fit_count_vec(tracks)

def test_predit():
    pids, challenge_data = createTrackDict.process_mpd(app_settings.CHALLENGE_SET, 1)

    challenge_dict = {}
    for pid, track in zip(pids, challenge_data):
        challenge_dict[pid] = track.split()

    predictions = predit_doc2vec_pca(challenge_dict)

if __name__ == '__main__':
    main()
