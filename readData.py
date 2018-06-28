import json
import re
import time
import app_settings
from collections import Counter

import matplotlib.pyplot as plt
from gensim.models import Doc2Vec
from gensim.models import Word2Vec
from gensim.models.doc2vec import TaggedDocument
# import nltk
# nltk.download('punkt')
from sklearn.manifold import TSNE

onlyfiles = app_settings.MPD_FILENAMES
file_count=1000
train_data = onlyfiles[:file_count]
test_data = onlyfiles[file_count:int(file_count+file_count*0.2)]
counted = Counter()


def extract_playlist_info(playlist):
    name = playlist["name"]
    songs = playlist["tracks"]
    song_ids = [str(s["track_uri"]) for s in songs]
    # song_ids = [str(s["album_uri"]) for s in songs]

    song_names = [str(s["track_name"]) for s in songs]
    # song_ids = " ".join(song_ids)
    # tokenized_text = word_tokenize(song_ids)
    return (name+" "+str(playlist["pid"]), (song_names, song_ids))


def searchForId(playlists):
    id="spotify:track:0mt02gJ425Xjm7c3jYkOBn"
    for p in playlists:
        pl = extract_playlist_info(p)
        if id in pl[1][1]:
            print("yeaaaahhhh")

def generator_playlists(nr_of_files):
    for f in onlyfiles[:nr_of_files]:
        print(f)
        fullPath = app_settings.MPD_PATH + str(f)
        data = json.load(open(fullPath))
        playlists=[]
        searchForId(data["playlists"])
        for playlist in data["playlists"]:
            pl=extract_playlist_info(playlist)
            onlyIds=pl[1][1]
            # onlyIds=" ".join(onlyIds)
            yield onlyIds

def data_to_word2vec(files,dimension,max_vocab_size):
    gen=generator_playlists(files)
    model=Word2Vec(size=dimension,min_count=1,max_vocab_size=max_vocab_size)
    model.build_vocab(gen)
    # print(model.wv['spotify:track:0mt02gJ425Xjm7c3jYkOBn'])
    gen = generator_playlists(files)
    model.train(gen,total_examples=model.corpus_count,epochs=model.epochs)
    # model = Word2Vec(gen, min_count=1)
    # print(model.wv.vocab['spotify:track:0mt02gJ425Xjm7c3jYkOBn'])
    # print(model.wv.most_similar(positive="spotify:track:0mt02gJ425Xjm7c3jYkOBn"))
    return model

#retruns list of all playlists in file
def get_file_contents(files):
    for f in onlyfiles[:files]:
        print(f)
        fullPath = app_settings.MPD_PATH + str(f)
        data = json.load(open(fullPath))
        # playlists=[]
        pls= [pl for pl in data["playlists"]]
        yield pls

# data_to_word2vec()
def get_docs(files):
    for f in onlyfiles[:files]:
        print(f)
        fullPath = app_settings.MPD_PATH + str(f)
        data = json.load(open(fullPath))
        # playlists=[]
        for playlist in data["playlists"]:
            pl=extract_playlist_info(playlist)
            # playlists.append(pl)
            pl=pl[1][1]
            pl=" ".join(pl)
            yield pl

        # class tagged_docs:
        #     def __iter__(self):
        #         for f in files:
        #             print(f)
        #             fullPath = PATH + str(f)
        #             data = json.load(open(fullPath))
        #             for playlist in data["playlists"]:
        #                 name = playlist["name"]
        #                 songs = playlist["tracks"]
        #                 song_ids = [str(s["track_uri"]) for s in songs]
        #                 # song_ids = " ".join(song_ids)
        #                 # tokenized_text = word_tokenize(song_ids)
        #                 doc = TaggedDocument( song_ids,[name])
        #                 yield doc
        #

def trainModel(files):

        class tagged_docs:
            def __iter__(self):
                for f in files:
                    print(f)
                    fullPath = app_settings.MPD_PATH + str(f)
                    data = json.load(open(fullPath))
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


        # pprint(data)
        # counted+=readTitles.titles_to_list(data)
        # print(counted)
        cnt = Counter(counted)
        # docs=memorySavingReader.tagged_docs(data)
        docs = tagged_docs()

        # model = Doc2Vec(docs, vector_size=100, window=8, min_count=5, workers=4)
        vecSize=300
        window=2
        model=Doc2Vec(vector_size=vecSize, window=window,workers=8)
        model.build_vocab(docs)
        start = time.clock()
        print(model.iter)
        model.train(docs, total_examples=model.corpus_count, epochs=model.iter)
        print("training took", time.clock() - start)
        # model.train(docs)
        cnt = Counter(counted)
        print(cnt)
        #model.save("fullModeD2V"+str(vecSize)+"D"+str(window)+"W")
        f=open("fullModeD2V"+str(vecSize)+"D"+str(window)+"W","wb")
        pickle.dump(model,f)
        return model


def testModel(files,model):
    for f in files:

        fullPath = app_settings.MPD_PATH + str(f)
        data = json.load(open(fullPath))
        for playlist in data["playlists"]:
            pid=playlist["pid"]
            name = playlist["name"]
            songs = playlist["tracks"]
            song_ids = [str(s["track_uri"]) for s in songs]
            # song_ids=" ".join(song_ids)
            # tokenized_text = word_tokenize(song_ids)
            # inferred_vector = model.infer_vector(TaggedDocument("","Chill"))
            # print(model.docvecs.most_similar(positive=['Chill'], negative=[], topn=10))
            inferred_vector = model.infer_vector(song_ids[0])
            inferred_vector = model.infer_vector(TaggedDocument(song_ids[0],name))
            inferred_vector2 = model.infer_vector(song_ids[0])
            inferred_vector3 = name



            sims = model.docvecs.most_similar([inferred_vector],topn=10)
            print(name)
            import compare
            for tup in sims:
                try:
                    mostSimilarList=int(str(tup[0]).split(" ")[-1])
                    compare.compare_pids(pid,mostSimilarList)
                except:
                    print(tup)
            print("song and name")
            print(sims)
            print("only song")
            print(model.docvecs.most_similar([inferred_vector2],topn=10))
            print("only name")
            tags = model.docvecs.doctags
            if name not in tags:
                print("name not in tags")
            else:
                print(model.docvecs.most_similar(name,topn=10))



# model=trainModel(onlyfiles)
# model=Doc2Vec.load("fullModel")
# print("loading done")
# testModel(onlyfiles,model)


def firstn(arr):
    for a in arr:
        yield a

def plot(data):
    fig, ax = plt.subplots()
    for twoDimVec in data:
        ax.scatter(twoDimVec[0], twoDimVec[1])
    print("show")
    plt.show()

def tsne_plot(model):
    vocab = list(model.docvecs.doctags)[:1000]
    X = model.docvecs[vocab]
    tsne = TSNE(n_components=2)
    print("try to fit transfo tsne")
    X_tsne = tsne.fit_transform(X[:1000])
    print("transfo done")
    import pandas as pd
    df = pd.DataFrame(X_tsne, index=vocab, columns=['x', 'y'])

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(df['x'], df['y'])
    for word, pos in df.iterrows():
        ax.annotate(word, pos)
    plt.show()



def clustering(model):

    from sklearn.cluster.affinity_propagation_ import AffinityPropagation
    tsne_plot(model)


    X=model.docvecs.doctag_syn0


    from sklearn.decomposition import PCA

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X)


    print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))

    print("fitt clusters")
    af = AffinityPropagation(preference=-500).fit(pca_result[:1000])
    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    print("af clusters: ",n_clusters_)

    plot(pca_result[:1000])


def create_lookup():
    lookupSet=dict()
    for f in onlyfiles:
        print(f)
        fullPath = app_settings.MPD_PATH + str(f)
        data = json.load(open(fullPath))
        playlists=[]
        for playlist in data["playlists"]:
            pl=extract_playlist_info(playlist)
            lookup=(pl[0],f)

            lookupSet[pl[0]]=f
    import pickle
    dbfile = open('lookupDict', 'wb')
    pickle.dump(lookupSet, dbfile)

import pickle

# create_lookup()

def get_playlist_name_dict():
    lookupDict = pickle.load(open("lookupDict", "rb"))
    return lookupDict


def search_playlist_name(name):
    lookupDict = pickle.load(open("lookupDict", "rb"))
    # print("do")
    i=0
    for k in lookupDict:
        if name in k:
            i+=1
            # if name in k.split(" "):
                # print(k.split(" "))
                # print(k)

    # print(i)
    return i

def search_playlist_names(names,regex=True):
    lookupDict = pickle.load(open("lookupDict", "rb"))
    # results=[[query_pl_name,count,match_ids]
    results=[]
    # print("do")
    j=0
    for name in names:
        start=time.clock()
        i=0
        matches=[]
        for k in lookupDict:
            if regex:
                t1=re.sub(r'[^\w]', ' ', name).lower().strip()
                t2=re.sub(r'[^\w]', ' ', k).lower().strip()
            else:
                t1 =  name.lower().strip()
                t2 = k.lower().strip()

            if t1 in t2:
                i+=1
                matches.append(k)

        results.append([name,i,matches])
        print("this will take (minutes) ",(time.clock()-start)*len(names)/60)
        print(j," / ",len(names))
        j+=1

    # print(i)
    return results

# search_playlist_name("wo")
# clustering(model)


# import compare
#
# docs=[d for d in get_docs(test_data)]
# pl1=docs[1]
# for d in docs:
#     compare.compare_playlist_equality(pl1,d)



# check which sets are most similar

# new name as input -> which is closest name from playlists



# trainModel(onlyfiles)

# find_playlist(999)
# tsne_plot(model)
