import spacy
import pprint
import random
import glob

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('mode', help='The operating modes for lyricHelper are: download, list, train, write')
parser.add_argument('--api_token', help='API key for genius lyrics, used only in download mode ( https://genius.com/api-clients )')
parser.add_argument('--download_list', help='Location of song download list, defaults to downloadList.txt')
parser.add_argument('--download_dir', help='Where to place/find downloaded songs, defaults to lyrics/')
parser.add_argument('--wordbank_dir', help='Where to place/find learned words, defaults to word_bank.json')
parser.add_argument('--base_song', help='Song to be used for reference in writing. Chooses at random from --download_dir if not defined')
args = parser.parse_args()
import pickle

from bs4 import BeautifulSoup
import requests
import urllib.request as urllib2
import json


nlp = spacy.load("en_core_web_sm")

word_bank = dict()

def getSongFromWeb(search_term):
    _URL_API = "https://api.genius.com/"
    _URL_SEARCH = "search?q="
    querystring = _URL_API + _URL_SEARCH + urllib2.quote(search_term)
    request = urllib2.Request(querystring)
    client_access_token = args.api_token
    request.add_header("Authorization", "Bearer " + client_access_token)
    request.add_header("User-Agent", "")
    response = urllib2.urlopen(request, timeout=3)
    encoding = response.info().get_content_charset('utf-8')
    json_obj = json.loads(response.read().decode(encoding))
    song_info = json_obj['response']['hits'][0]['result']
    page = requests.get(song_info['url'])
    html = BeautifulSoup(page.text, "html.parser")
    lyrics = html.find("div", class_="lyrics").get_text()
    song_info = json_obj['response']['hits'][0]['result']
    song_title = song_info['title'].lower().replace(" ", "-")
    song_artist = song_info['primary_artist']['name'].lower().replace(" ", "-")
    with open(args.download_dir + '/' + song_artist + "." + song_title, 'w') as file:
        file.write(lyrics)

def learnWords(files):
    for file_name in files:
        with open(file_name) as file:
            for line in file:
                sentance = line.strip()
                doc = nlp(sentance)
                for i in range(0, len(doc)):
                    if(token.text.strip().lower() == "chorus" or token.text.strip().lower() == "verse"):
                        continue
                    token = doc[i]
                    if token.tag_ not in word_bank.keys():
                        word_bank[token.tag_] = dict()
                    if token.dep_ not in word_bank[token.tag_].keys():
                       word_bank[token.tag_][token.dep_] = []
                    word_bank[token.tag_][token.dep_].append(token.text.lower())

def writeSong(baseSong):
    print("BASED ON: " + baseSong)
    print()
    written_lyrics = dict()
    with open(baseSong) as file:
        for line in file:
            sentance = line.strip()
            doc = nlp(sentance)
            for token in doc:
                sub = token.text
                start_offset = " "
                if token.tag_ in word_bank.keys():
                    if token.dep_ in word_bank[token.tag_].keys():
                        possible_subs = word_bank[token.tag_][token.dep_]
                        sub_idx = random.randrange(len(possible_subs))
                        sub = possible_subs[sub_idx]
                    #punctuation is hard
                    if "'" in sub:
                        #start_offset = ""
                        sub = token.text
                    if "," in token.text or  '"' in token.text:
                        start_offset = ""
                    #if a line is repeated in a song I wanted it to be repeated here too
                    if(token.text in written_lyrics.keys()):
                        sub = written_lyrics[token.text]
                    else:
                        written_lyrics[token.text] = sub
                    
                    sub = sub.lower()
                print(start_offset  + sub.replace("-", " "), end="")
            print()

def writeDictToFile(filename):
    with open(filename, 'wb') as outfile:
        pickle.dump(word_bank, outfile)
    
def readDictFromFile(filename):
    global word_bank
    with open(filename, 'rb') as infile:
        word_bank = pickle.load(infile)

if __name__ == "__main__":
    mode = args.mode.lower()
    if(args.download_list == None):
        args.download_list = "downloadList.txt"
    if(args.download_dir == None):
        args.download_dir = "lyrics"
    if(args.wordbank_dir == None):
        args.wordbank_dir = "word_bank.gar"
    if(args.base_song == None):
        songs_to_learn = glob.glob(args.download_dir + "/*")
        song_idx = random.randrange(len(songs_to_learn))
        args.base_song = songs_to_learn[song_idx]
    if(args.api_token == None):
        args.api_token = ""

    if(mode == "list"):
        readDictFromFile(args.wordbank_dir)
        print(word_bank)
    elif(mode == "download"):
        if(args.api_token == ""):
            print("GENERATE API CLIENT TOKEN FROM https://genius.com/api-clients OR YOU WILL HAVE A BAD TIME")
            print("pass via --api_token. Run ./lyricHelper for more options")
            exit()
        else:
            print("api_token: " + args.api_token)
        with open(args.download_list) as file:
            for song in file:
                getSongFromWeb(song)
    elif(mode == "train"):
        songs_to_learn = glob.glob(args.download_dir + "/*")
        learnWords(songs_to_learn)
        writeDictToFile(args.wordbank_dir)
    elif(mode == "write"):
        readDictFromFile(args.wordbank_dir)
        writeSong(args.base_song)