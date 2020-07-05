import glob
from dataclasses import dataclass

@dataclass
class PartOfSpeech:
    name: str
    ordered: dict
    unordered: set

contraction_list = dict()
adjectives = None
adverbs = None
nouns = None
verbs = None
pronouns = None

def loadPartOfSpeech(name):
    ordered_list = {1:set(), 2:set(), 3:set(), 4:set()}
    unordered_list = set()
    files_to_read = glob.glob("partsOfSpeech/" + name + "/*")
    for file_name in files_to_read:
        with open(file_name) as file:
            for line in file:
                if(len(file_name) > 8):
                    if(file_name.split("/")[-1][1:9] == "syllable"):
                        ordered_list[int(file_name.split("/")[-1][0])].add(line.strip())
                    else:
                        unordered_list.add(line.strip())
    word_list = PartOfSpeech(name, ordered_list, unordered_list)
    return word_list

def getContractions():
    with open("partsOfSpeech/contractions.txt") as file:
        for line in file:
            parts = line.split(" = ")
            contraction_list[parts[0]] = line[len(parts[0])+2:].strip()

def checkInPartOfSpeech(word, partofspeech):
    for i in range(1,5):
        if word in partofspeech.ordered[i]:
            return i
    if word in partofspeech.unordered:
        return 0
    return -1
    

def getWordType(word):
    for part in [pronouns,adjectives,adverbs,verbs,nouns]:
        check = checkInPartOfSpeech(word, part)
        if check != -1:
            return part.name + "(" + str(check) + ")"
    return "unknown"

def readSong():
    with open("lyrics/american-football.never-meant") as file:
        for line in file:
            for word in line.split(" "):
                cleaned_word = word.lower().strip()
                if(cleaned_word in contraction_list):
                    cleaned_word = contraction_list[cleaned_word]
                #with the contractions sometimes one word becomes two
                word_type = ""
                for final_word in cleaned_word.split(" "):
                    word_type += getWordType(final_word)
                print(cleaned_word + "(" + word_type + ")", end=" ")
            print()

print("Loading Contractions")
getContractions()
print("Loading Adjectives")
adjectives = loadPartOfSpeech("adjectives")
print("Loading Adverbs")
adverbs = loadPartOfSpeech("adverbs")
print("Loading Nouns")
nouns = loadPartOfSpeech("nouns")
print("Loading Verbs")
verbs = loadPartOfSpeech("verbs")
print("Loading Pronouns")
pronouns = loadPartOfSpeech("pronouns")
print("done.")
print()
#print(getWordType("leech"))
readSong()