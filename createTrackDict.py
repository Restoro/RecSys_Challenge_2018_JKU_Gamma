from collections import Counter, defaultdict
from gensim.models.doc2vec import TaggedDocument
from multiprocessing import Pool, Value
import glob
import json
import pickle_utility
import app_settings

def create_pid_dict(fileCount):
    pids, tracks = process_mpd(app_settings.MPD_SET, fileCount)

    print("Concat lists")
    pid_dict = {}

    for pid, track in zip(pids, tracks):
        pid_dict[pid] = track

    print("Dump")
    pickle_utility.dump(pid_dict, "pidtotracks")
    return

def process_mpd(path, files):
    count = 0
    fileList = glob.glob(path);

    p = Pool()

    counter = 1;
    playlist_tracks = []
    playlist_pids = []

    for result in p.imap_unordered(process_file, fileList[:files]):
        print("Apppend result from process {0}...".format(counter))
        playlist_pids.extend(result[0])
        playlist_tracks.extend(result[1])
        counter += 1

    p.close()
    p.join()
    return playlist_pids, playlist_tracks

def process_file(filePath):
    f = open(filePath)
    js = f.read()
    f.close()
    mpd_slice = json.loads(js)
    playlists = process_mpd_file(mpd_slice)

    print("Processed File: {0}".format(filePath))
    return playlists

def process_mpd_file(mpd_slice):
    playlist_pids = []
    playlists = []
    for playlist in mpd_slice['playlists']:
        pl = extract_playlist_info(playlist)
        #pl = pl[1][1]
        playlist_pids.append(pl[1])
        joinPl = " ".join(pl[2][1])
        playlists.append(joinPl)
    return (playlist_pids, playlists)

def extract_playlist_info(playlist):
    name = playlist.get("name","")
    songs = playlist["tracks"]
    song_ids = [str(s["track_uri"]) for s in songs]
    # song_ids = [str(s["artist_uri"]) for s in songs]

    song_names = [str(s["track_name"]) for s in songs]
    # song_ids = " ".join(song_ids)
    # tokenized_text = word_tokenize(song_ids)
    return (name+" "+str(playlist["pid"]), playlist["pid"], (song_names, song_ids))

def generate_tagged_docs(files):
    p = Pool()
    docs = []
    counter = 0

    for result in p.imap_unordered(process_docs_file, files):
        print("Apppend result from process {0}...".format(counter))
        counter += 1
        docs.extend(result)

    return docs

def process_docs_file(file):
    f = open(file)
    js = f.read()
    f.close()
    json_file = json.loads(js)

    docs = []
    for playlist in json_file['playlists']:
        tg = generate_tagged_document(playlist)
        docs.append(tg)
    print("Processed File: {0}".format(file))
    return docs

def generate_tagged_document(playlist):
    name = playlist["name"]
    name=[name+" "+str(playlist["pid"]),name]
    songs = playlist["tracks"]
    song_ids = [str(s["track_uri"]) for s in songs]
    doc = TaggedDocument( song_ids,name)
    return doc

if __name__ == '__main__':
    create_pid_dict(10)