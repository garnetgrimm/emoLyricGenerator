import tkinter as tk
import lyricHelper

lyricHelper.readDictFromFile(lyricHelper.wordbank_dir)
song = lyricHelper.writeSongRaw("")
songLine = 1
songPos = 0

def setButtons():
    global songLine
    global songPos
    global listbox

    line = song[songLine].split()
    while(len(line) < 1):
        text2.insert(tk.END, "\n")
        songLine +=1
        line = song[songLine].split()

    songPos += 1
    if(songPos >= len(line)):
        text2.insert(tk.END, "\n")
        songLine += 1
        songPos = 0

    tag = line[songPos].split(".")
    
    listbox.delete(0, tk.END)
    listbox.insert(tk.END, "Skip")
    listbox.insert(tk.END, "New Line")
    mylist = list(dict.fromkeys(lyricHelper.word_bank[tag[0]][tag[1]]))
    for index in range(len(mylist)):
        possible_sub = mylist[index]
        listbox.insert(tk.END, possible_sub)

def setTextInput(event=""):
    global text2
    global songLine
    global songPos
    text2.configure(state='normal')
    text = listbox.get(tk.ACTIVE)
    if(text == "New Line"):
        songLine += 1
        songPos = 0
        text2.insert(tk.END, "\n")
    elif(text == "Skip"):
        text2.insert(tk.END, " ")
    else:
        text2.insert(tk.END, text + " ")
    text2.configure(state='disabled')
    setButtons()

def on_configure(event):
    global canvas
    canvas.configure(scrollregion=canvas.bbox('all'))


root = tk.Tk()
root.geometry("640x480")

bottomframe = tk.Frame(root)
bottomframe.pack(side = tk.LEFT, fill=tk.Y)
scrollbar = tk.Scrollbar(bottomframe)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox = tk.Listbox(bottomframe)
listbox.pack(side=tk.LEFT, fill=tk.Y)
button1 = tk.Button(root, text ="Select", command = setTextInput)
button1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

root.bind('<Return>', setTextInput)

scroll = tk.Scrollbar(root)
text2 = tk.Text(root, height=20, width=70)
text2.configure(yscrollcommand=scroll.set)
text2.tag_configure('bold_italics', font=('Arial', 12, 'bold', 'italic'))
text2.tag_configure('big', font=('Verdana', 20, 'bold'))
text2.tag_configure('color',foreground='#476042',font=('Tempus Sans ITC', 12, 'bold'))
text2.pack(side=tk.LEFT)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

text2.insert(tk.END, "BASED ON: " + song[0] + "\n")

setButtons()

root.mainloop()