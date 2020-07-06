import glob
from dataclasses import dataclass
import random
import os.path
from os import path
import pickle

@dataclass
class PartOfSpeech:
    ordered: dict
    unordered: set

lang = dict()
lang["contractions"] = dict()
lang["adjectives"] = None
lang["adverbs"] = None
lang["nouns"] = None
lang["verbs"] = None
lang["pronouns"] = None

seen = dict()
seen["contractions"] = dict()
seen["adjectives"] = PartOfSpeech({1:list(), 2:list(), 3:list(), 4:list()}, list())
seen["adverbs"] = PartOfSpeech({1:list(), 2:list(), 3:list(), 4:list()}, list())
seen["nouns"] = PartOfSpeech({1:list(), 2:list(), 3:list(), 4:list()}, list())
seen["verbs"] = PartOfSpeech({1:list(), 2:list(), 3:list(), 4:list()}, list())
seen["pronouns"] = PartOfSpeech({1:list(), 2:list(), 3:list(), 4:list()}, list())
seen["unknown"] = list()

def writeDictToFile(filename):
    with open(filename, 'wb') as outfile:
        pickle.dump(seen, outfile)
    
def readDictFromFile(filename):
    global word_bank
    with open(filename, 'rb') as infile:
        seen = pickle.load(infile)

def loadPartOfSpeech(name):
    ordered_list = {1:list(), 2:list(), 3:list(), 4:list()}
    unordered_list = list()
    files_to_read = glob.glob("partsOfSpeech/" + name + "/*")
    for file_name in files_to_read:
        with open(file_name) as file:
            for line in file:
                if(len(file_name) > 8):
                    if(file_name.split("/")[-1][1:9] == "syllable"):
                        ordered_list[int(file_name.split("/")[-1][0])].append(line.strip())
                    else:
                        unordered_list.append(line.strip())
    word_list = PartOfSpeech(ordered_list, unordered_list)
    return word_list

def getContractions():
    contlist = dict()
    with open("partsOfSpeech/contractions.txt") as file:
        for line in file:
            parts = line.split(" = ")
            contlist[parts[0]] = line[len(parts[0])+2:].strip()
    return contlist

def checkInPartOfSpeech(word, partofspeech):
    for i in range(1,5):
        if word in partofspeech.ordered[i]:
            return i
    if word in partofspeech.unordered:
        return 0
    return -1
    
def getEnding(word):
    ###THIS COULD BE BETTER
    #THERE ARE ACTUAL RULES FOR THIS
    if(word[-1:] == "'s"):
        return "'s"
    if(word[-3:] == "ing"):
        return "ing"
    if(word[-2:] == "ed"):
        return "ed"
    return "none"

def megaStrip(word):
    return word.replace(",","").replace("!","").replace("?","").replace("\"","").replace("-","")

def getRoot(word):
    ###THIS COULD BE BETTER
    #THERE ARE ACTUAL RULES FOR THIS
    ending = getEnding(word)
    if(ending == "none"):
        return megaStrip(word)
    else:
        return megaStrip(word)[:-len(ending)]

def getWordType(word):
    word = megaStrip(word)
    ending = getEnding(word)
    for part in ["pronouns", "adjectives", "adverbs", "verbs", "nouns"]:
        if(isinstance(lang[part],PartOfSpeech)):
            check = checkInPartOfSpeech(getRoot(word), lang[part])
            if check != -1:
                return part + "." + str(check) + "." + ending
    return "unknown"

def getStrippedSong(song_file):
    strippedLyrics = ""
    with open(song_file) as file:
        for line in file:
            for word in line.split(" "):
                cleaned_word = word.lower().strip()
                if(cleaned_word in lang["contractions"]):
                    cleaned_word = lang["contractions"][cleaned_word]
                #with the contractions sometimes one word becomes two
                for final_word in cleaned_word.split(" "):
                    word_type = getWordType(final_word)
                    if(word_type.split(".")[0] == "unknown"):
                        #print(final_word)
                        seen["unknown"].append(final_word)
                        strippedLyrics += "unknown." + final_word + " "
                    else:
                        type_parts = word_type.split(".")
                        syll_count = int(type_parts[1])
                        if(syll_count > 0):
                            seen[type_parts[0]].ordered[syll_count].append(getRoot(final_word))
                        else:
                            seen[type_parts[0]].unordered.append(getRoot(final_word))
                        strippedLyrics += word_type + " "
            strippedLyrics += "\n"
    return (strippedLyrics)

def getNewSong(strippedSong):
    newLyrics = ""
    written_lines = dict()
    for line in strippedSong.split("\n"):
        newSentance = ""
        if line.strip() in written_lines:
            newSentance = written_lines[line.strip()]
        else:
            for word in line.split(" "):
                cleaned_word = word.strip()
                info = cleaned_word.split(".")
                word_type = info[0]
                if(len(info) >= 2):
                    if(word_type == "unknown"):
                        newSentance += info[1] + " "
                    else:
                        syll_count = int(info[1])
                        ending = ""
                        if(info[2] != "none"):
                            ending = info[2]
                        new_word = ""
                        if(syll_count == 0):
                            new_word = random.choice(tuple(seen[word_type].unordered)) + ending
                        else:
                            new_word = random.choice(tuple(seen[word_type].ordered[syll_count]))
                            if(new_word[-1] == "e"):
                                if(ending == "ing" or ending == "ed"):
                                    new_word = new_word[:-1]
                            new_word += ending
                        newSentance += new_word + " "
        written_lines[line.strip()] = newSentance
        newLyrics += newSentance + "\n"
    return newLyrics


print("Learning to English.")
print("Loading Pronouns")
lang["pronouns"] = loadPartOfSpeech("pronouns")
print("Loading Adverbs")
lang["adverbs"] = loadPartOfSpeech("adverbs")
print("Loading Adjectives")
lang["adjectives"] = loadPartOfSpeech("adjectives")
print("Loading Verbs")
lang["verbs"] = loadPartOfSpeech("verbs")
print("Loading Nouns")
lang["nouns"] = loadPartOfSpeech("nouns")
print("Loading Contractions")
lang["contractions"] = getContractions()
print("done.")
print()
songs_to_learn = glob.glob("lyrics/*")
if(path.exists("word_bank.gar")):
    print("found previous music")
    readDictFromFile("word_bank.gar")
else:
    print("listening to new music.")
    for song in songs_to_learn:
        getStrippedSong(song)
print("done.")
print()
song = random.choice(songs_to_learn)
#song = "lyrics/cap’n-jazz.bluegrassish"
print("Writing new song based on " + song)
print()
print(getNewSong(getStrippedSong(song)))

print(seen["pronouns"])
##todo - verbs and nouns have different es rules