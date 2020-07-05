import spacy
import pprint
import random
import glob

import argparse
import pickle

from bs4 import BeautifulSoup
import requests
import urllib.request as urllib2
import json

nlp = spacy.load("en_core_web_sm")
word_bank = dict()
rhyme_list = None

download_list = "downloadList.txt"
download_dir = "lyrics"
wordbank_dir = "word_bank.gar"
api_token = ""
base_song = ""
proper = False

contraction_list = dict()
rev_contraction_list = dict()

def getContractions():
    global contraction_list
    with open("contractions.txt") as file:
        for line in file:
            parts = line.split(" = ")
            seperated_word = parts[1]
            cont_word = parts[0]
            contraction_list[cont_word] = seperated_word_list
            rev_contraction_list[seperated_word] = cont_word

def getSongFromWeb(search_term):
    _URL_API = "https://api.genius.com/"
    _URL_SEARCH = "search?q="
    querystring = _URL_API + _URL_SEARCH + urllib2.quote(search_term)
    request = urllib2.Request(querystring)
    client_access_token = api_token
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
    with open(download_dir + '/' + song_artist + "." + song_title, 'w') as file:
        file.write(lyrics)

def learnWords(files):
    getContractions()
    for file_name in files:
        with open(file_name) as file:
            for line in file:
                easier_sentance = ""
                for word in line.split(" "):
                    cleaned_word = word.lower().strip()
                    if(cleaned_word in contraction_list):
                        easier_sentance += contraction_list[cleaned_word] + " "
                    else:
                        easier_sentance += cleaned_word + " "
                doc = nlp(easier_sentance)
                for i in range(0, len(doc)):
                    token = doc[i]
                    if(token.text.strip().lower() == "chorus" or token.text.strip().lower() == "verse"):
                        continue
                    if token.tag_ not in word_bank.keys():
                        word_bank[token.tag_] = dict()
                    if token.dep_ not in word_bank[token.tag_].keys():
                       word_bank[token.tag_][token.dep_] = []
                    word_bank[token.tag_][token.dep_].append(token.text.lower())

def writeSongRaw(baseSong):
    if(baseSong == ""):
        songs_to_learn = glob.glob(download_dir + "/*")
        song_idx = random.randrange(len(songs_to_learn))
        baseSong = songs_to_learn[song_idx]
    return_str = []
    return_str.append(baseSong)
    written_lyrics = dict()
    with open(baseSong) as file:
        for line in file:
            sentance = line.strip()
            doc = nlp(sentance)
            new_sentance = ""
            for token in doc:
                new_sentance += (token.tag_ + "." + token.dep_ + " ")
            return_str.append(new_sentance)
    return return_str
                

def getAllWords(d,depth=0):
    finalList = []
    if(isinstance(d, dict)):
        for key in d.keys():
            finalList = finalList + getAllWords(d[key],depth+1)
        return finalList
    else:
        return d

def getRhymeRating(word1, word2, rating=1):
    if(word1 == word2):
        return len(word1)
    if(word1[-rating:] == word2[-rating:]):
        return getRhymeRating(word1,word2,rating+1)
    else:
        return rating-1

def writeSong(baseSong):
    if(baseSong == ""):
        songs_to_learn = glob.glob(download_dir + "/*")
        song_idx = random.randrange(len(songs_to_learn))
        baseSong = songs_to_learn[song_idx]
    print("BASED ON: " + baseSong)
    print()
    written_lyrics = dict()
    lastLine = ""
    lastLastLine = ""
    with open(baseSong) as file:
        for line in file:
            sentance = line.strip()
            new_sentance = ""
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
                        if(proper):
                            start_offset = ""
                        else:
                            sub = ""
                    if "," in token.text or  '"' in token.text:
                        start_offset = ""
                    #if a line is repeated in a song I wanted it to be repeated here too
                    if(token.text in written_lyrics.keys()):
                        sub = written_lyrics[token.text]
                    else:
                        written_lyrics[token.text] = sub
                    sub = sub.lower()
                new_sentance += start_offset  + sub.replace("-", " ")
            #look for rhymes at the end
            rhyme_end = ""
            if(rhyme_list is not None and getRhymeRating(lastLastLine, lastLine) == 0):
                rhyme_rating = dict()
                for pot_sub in rhyme_list:
                    if(lastLine[-len(pot_sub):] != pot_sub):
                        rating = getRhymeRating(pot_sub, lastLine)
                        rhyme_rating[pot_sub] = rating
                best_rhymes = sorted(rhyme_rating.items(), key=lambda x: x[1], reverse=True)
                if(int(best_rhymes[0][1]) != 0):
                    rhyme_end = best_rhymes[0][0]
            split_sentace = new_sentance.split(" ")
            split_sentace[-1] = rhyme_end
            split_sentace = [x for x in split_sentace if x != " "]
            new_sentance = ' '.join(split_sentace)
            #check for contractions

            print(new_sentance)
            lastLastLine = lastLine
            lastLine = new_sentance.strip()

def writeDictToFile(filename):
    with open(filename, 'wb') as outfile:
        pickle.dump(word_bank, outfile)
    
def readDictFromFile(filename):
    global word_bank
    with open(filename, 'rb') as infile:
        word_bank = pickle.load(infile)

def getWordList():
    songs_to_learn = glob.glob(download_dir + "/*")
    learnWords(songs_to_learn)
    allwords = getAllWords(word_bank)
    lowers = [x.lower() for x in allwords]
    return list(dict.fromkeys(lowers))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='The operating modes for lyricHelper are: download, list, train, write')
    parser.add_argument('--api_token', help='API key for genius lyrics, used only in download mode ( https://genius.com/api-clients )')
    parser.add_argument('--download_list', help='Location of song download list, defaults to downloadList.txt')
    parser.add_argument('--download_dir', help='Where to place/find downloaded songs, defaults to lyrics/')
    parser.add_argument('--wordbank_dir', help='Where to place/find learned words, defaults to word_bank.json')
    parser.add_argument('--base_song', help='Song to be used for reference in writing. Chooses at random from --download_dir if not defined')
    parser.add_argument('--rhyme', help='Try to generate ryhmes in the song. Will take slightly longer', action='store_true')
    parser.add_argument('--proper', help='Try to do things like You\'ll and I\'m', action='store_true')
    args = parser.parse_args()

    mode = args.mode.lower()
    if(args.download_list != None):
        download_list = args.download_list
    if(args.download_dir != None):
        download_dir = args.download_dir
    if(args.wordbank_dir != None):
        wordbank_dir = args.wordbank_dir
    if(args.base_song != None):
        base_song = args.base_song
    if(args.api_token != None):
        api_token = args.api_token
    if(args.rhyme != None):
        rhyme_list = getWordList()
    if(args.proper != None):
        proper = True

    if(mode == "list"):
        readDictFromFile(wordbank_dir)
        print(word_bank)
    elif(mode == "download"):
        if(api_token == ""):
            print("GENERATE API CLIENT TOKEN FROM https://genius.com/api-clients OR YOU WILL HAVE A BAD TIME")
            print("pass via --api_token. Run ./lyricHelper for more options")
            exit()
        else:
            print("api_token: " + api_token)
        with open(download_list) as file:
            for song in file:
                getSongFromWeb(song)
    elif(mode == "train"):
        songs_to_learn = glob.glob(download_dir + "/*")
        learnWords(songs_to_learn)
        writeDictToFile(wordbank_dir)
    elif(mode == "write"):
        readDictFromFile(wordbank_dir)
        writeSong(base_song)
