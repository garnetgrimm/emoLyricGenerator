import spacy
import pprint
import random
import glob

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
    client_access_token = "qKMFkRZXFe0q_L6TCfpfn84MTwKMAbAp_Fqxsu7tgTfjGj8nGXw2aTf0CAHHA7Ez"
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
    with open('lyrics/' + song_artist + "." + song_title, 'w') as file:
        file.write(lyrics)

def learnWords(files):
    for file_name in files:
        with open(file_name) as file:
            for line in file:
                sentance = line.strip()
                doc = nlp(sentance)
                for i in range(0, len(doc)):
                    token = doc[i]
                    if token.tag_ not in word_bank.keys():
                        word_bank[token.tag_] = dict()
                    if token.dep_ not in word_bank[token.tag_].keys():
                       word_bank[token.tag_][token.dep_] = []
                    word_bank[token.tag_][token.dep_].append(token.text)

def writeSong(baseSong):
    written_lyrics = dict()
    with open(baseSong) as file:
        for line in file:
            sentance = line.strip()
            #print(sentance)
            doc = nlp(sentance)
            for token in doc:
                sub = token.text + "[]"
                if token.tag_ in word_bank.keys():
                    if token.dep_ in word_bank[token.tag_].keys():
                        possible_subs = word_bank[token.tag_][token.dep_]
                        sub_idx = random.randrange(len(possible_subs))
                        sub = possible_subs[sub_idx]
                    #punctuation is hard
                    if(token.pos_ == "PUNCT"):
                        sub = token.text
                    #if a line is repeated in a song I wanted it to be repeated here too
                    if(token.text in written_lyrics.keys()):
                        sub = written_lyrics[token.text]
                    else:
                        written_lyrics[token.text] = sub
                    
                    sub = sub.lower()
                print(sub, end=" ")
            print()

#getSongFromWeb("Modern Baseball Teers Over Beers")

songs_to_learn = glob.glob("lyrics/*")
learnWords(songs_to_learn)
song_idx = random.randrange(len(songs_to_learn))
writeSong(songs_to_learn[song_idx])

#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(word_bank)