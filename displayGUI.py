import tkinter as tk
import tkinter.ttk as ttk
import lyricHelper
import random
from functools import partial

lyricHelper.readDictFromFile(lyricHelper.wordbank_dir)
song = lyricHelper.writeSongRaw("")
songLine = 1
songPos = 0
buttons = []
activeRow = 0
activeCol = 0

def setButtons(row,col,word_type):
    global listbox
    global button1
    global activeRow
    global activeCol

    activeRow = row
    activeCol = col

    curr_word = word_type.split(".")
    tag = curr_word[0]
    dep = curr_word[1]

    listbox.delete(0, tk.END)
    listbox.insert(tk.END, "Skip")
    listbox.insert(tk.END, "New Line")
    lowers = [x.lower() for x in lyricHelper.word_bank[tag][dep]]
    mylist = list(dict.fromkeys(lowers))
    for index in range(len(mylist)):
        possible_sub = mylist[index]
        listbox.insert(tk.END, possible_sub)

def save():
    with open("song.txt", "w") as file:
        for y in range(0, len(buttons)):
            for x in range(0, len(buttons[y])):
                file.write(buttons[y][x].cget('text') + " ")
            file.write("\n")


def setTextInput(event=""):
    text = listbox.get(tk.ACTIVE)
    buttons[activeCol][activeRow].config(text=text)

def on_configure(event):
    global canvas
    canvas.configure(scrollregion=canvas.bbox('all'))


root = tk.Tk()
root.geometry("800x800")

ttk.Label(root, text=song[0]).pack(side=tk.BOTTOM)
tk.Button(root, text ="Save", command=save).pack(side=tk.BOTTOM)
tk.Button(root, text ="Select", command=setTextInput).pack(side=tk.BOTTOM)

bottomframe = tk.Frame(root)
bottomframe.pack(side = tk.LEFT, fill=tk.Y)
scrollbar = tk.Scrollbar(bottomframe)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox = tk.Listbox(bottomframe)
listbox.pack(side=tk.LEFT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

root.bind('<Return>', setTextInput)

style = ttk.Style()
style.configure('W.TButton', font = ('calibri', 5, 'bold', 'underline'), foreground = 'red') 
container = ttk.Frame(root)
canvas = tk.Canvas(container, height=700)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
for c in range(0, len(song)):
    buttons.append([])
    for r in range(0, len(song[c].split())):
        buttons[c].append([])
        curr_word = song[c].split()[r].split(".")
        tag = curr_word[0]
        dep = curr_word[1]
        sub = ""
        if tag in lyricHelper.word_bank.keys():
            if dep in lyricHelper.word_bank[tag].keys():
                possible_subs = lyricHelper.word_bank[tag][dep]
                sub_idx = random.randrange(len(possible_subs))
                sub = possible_subs[sub_idx]
        buttons[c][r] = ttk.Button(scrollable_frame, text=sub, style='W.TButton', command=partial(setButtons,r,c,song[c].split()[r]))
        buttons[c][r].grid(row=c, column=r, pady=0, padx=0)
container.pack(fill=tk.BOTH)
canvas.pack(side="left", fill=tk.BOTH, expand=True)
scrollbar.pack(side="right", fill="y")

root.mainloop()