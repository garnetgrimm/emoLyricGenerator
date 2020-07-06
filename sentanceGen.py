from dataclasses import dataclass
import random
import glob 

@dataclass
class Pronoun:
    subject: str
    obj:     str
    number:  str
    gender:  str
    person:  str

@dataclass 
class Verb:
    word:      str
    singular:  str
    princ:     str
    past:      str
    pastprinc: str

pronouns = []
verbs = []
nouns = []
quantities = ['a', 'a', 'the', 'one']
cord_conjunctions = ['for', 'and', 'but', 'or', 'yet', 'so']
propositions = []
adjectives = []
contractions = dict()

word_bank = dict()

def addToBank(word,word_type):
    if(word in word_bank):
        for types in word_bank[word].split(","):
            if types == word_type:
                return
        word_bank[word] += "," + word_type
    else:
        word_bank[word] = word_type
    
for word in quantities:
    addToBank(word,"quant")
for word in cord_conjunctions:
    addToBank(word,"conj")

with open("partsOfSpeech/contractions.txt") as file:
     for line in file:
        parts = line.split(" = ")
        contractions[parts[0]] = line[len(parts[0])+2:].strip()

with open("partsOfSpeech/pronouns/pronouns.txt") as file:
    for line in file:
        feilds = line.strip().split(",")
        pron = Pronoun(feilds[0],feilds[1],feilds[2],feilds[3],feilds[4])
        pronouns.append(pron)
        addToBank(feilds[0],"pronoun")
        addToBank(feilds[1],"pronoun")

with open("partsOfSpeech/verbs/verbsandtenses.txt") as file:
    for line in file:
        feilds = line.strip().split(",")
        fixed_feilds = []
        for feild in feilds:
            if feild == "" or feild == "-":
                fixed_feilds.append(feilds[0])
            else:
                fixed_feilds.append(feild)
        feilds = fixed_feilds
        verb = Verb(feilds[0],feilds[1],feilds[2],feilds[3],feilds[4])
        verbs.append(verb)
        addToBank(feilds[0], "verb.normal")
        addToBank(feilds[1], "verb.singular")
        addToBank(feilds[2], "verb.present")
        addToBank(feilds[3], "verb.past")
        addToBank(feilds[4], "verb.pastprinc")

with open("partsOfSpeech/nouns/nounlist.txt") as file:
    for line in file:
        if("ing" not in line):
            nouns.append(line.strip())
            addToBank(line.strip(),"noun")

with open("partsOfSpeech/propositions/propisitons.txt") as file:
    for line in file:
        propositions.append(line.strip())
        addToBank(line.strip(),"prop")
    
with open("partsOfSpeech/complete/28K adjectives.txt") as file:
    for line in file:
        if("ing" not in line):
            adjectives.append(line.strip())
            addToBank(line.strip(),"adj")


song = []
song_name = random.choice(glob.glob("lyrics/*"))
with open("lyrics/american-football.never-meant") as file:
    for line in file:
        sentance = "normal : "
        for word in line.strip().split():
            cleaned_word = word.lower()
            if(cleaned_word in contractions):
                cleaned_word = contractions[cleaned_word]
            for fixed_word in cleaned_word.split():
                if(fixed_word not in word_bank):
                    sentance += fixed_word + " "
                else:
                    sentance += word_bank[fixed_word] + " "
        song.append(sentance)

for line in song:
    sentance = ""
    reached_verb = False
    line_info = line.strip().split(" : ")
    if(len(line_info) > 1):
        words = line_info[1].split(" ")
        tense = line_info[0]
        for i in range(len(words)):
            part = random.choice(words[i].split(","))
            if(part.split(".")[0] == "verb"):
                reached_verb = True
                if(part.split(".")[1] == "normal"):
                    sentance += random.choice(verbs).word
                elif(part.split(".")[1] == "past"):
                    sentance += random.choice(verbs).past
                else:
                    sentance += random.choice(verbs).princ
                sentance += " "
            elif(part == "pronoun"):
                pronoun = random.choice(pronouns)
                if(reached_verb or tense == "normal"):
                    sentance += pronoun.subject
                    sentance += " "
                else:
                    sentance += pronoun.obj
                    sentance += " "
            elif(part == "noun"):
                sentance += random.choice(nouns)
                sentance += " "
            elif(part == "prop"):
                sentance += random.choice(propositions)
                sentance += " "
            elif(part == "quant"):
                quantity = random.choice(quantities)
                if(len(words) > i+1 and words[i+1] == "noun" and quantity == "a"):
                    noun = words[i+1]
                    if(noun[0] == 'a' or noun[0] == 'e' or noun[0] == 'i' or noun[0] == 'o' or noun[0] == 'u'):
                        quantity = "an"
                sentance += quantity
                sentance += " "
            elif(part == "adj"):
                sentance += random.choice(adjectives)
                sentance += " "
            elif(part == "conj"):
                sentance += random.choice(cord_conjunctions)
                sentance += " "
            else:
                sentance += part + " "
            
    print(sentance)