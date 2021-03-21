import tkinter as tk
from PIL import Image, ImageTk
import time
import os
#test

class Fullscreen():
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)  
        self.root.bind("<F11>",
                         lambda event: self.root.attributes("-fullscreen",
                                    not self.root.attributes("-fullscreen")))
        self.root.bind("<Escape>",
                         lambda event: self.root.attributes("-fullscreen",
                                    False))

def raise_frame(frame):
    frame.tkraise()


if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

#RootSettings
root = tk.Tk()

root.geometry("1280x900")
root.configure(bg="#131313")
f1 = tk.Frame(root, bg="#131313")
f2 = tk.Frame(root, bg="#131313")

#Positioniert alle frames mittig damit man ein startpunkt besitzt von dem man arbeiten kann 
for frame in (f1, f2):
    frame.place(relheight=1, relwidth=1)

    
#Background Picture
Logoimage = tk.PhotoImage(file="Logo2.gif")
background_label = tk.Label(f1, image=Logoimage).place(relwidth=1, relheight=1)
background_label2 = tk.Label(f2, image=Logoimage).place(relwidth=1, relheight=1)

#Einfaches Label
label = tk.Label(f1, text = "Bitte Nfc anlegen",fg="#9c3c30",bg="#131313", font=("Arial",20))#hab fpr die farben die Hex Nr verwendet weil ich es durhc ein programm herrausgefunden hab alsou sollte passen
label.place(relx=0.5,rely=0.65 ,anchor="center")

#Frame Nach dem erhalten des NFC`s
#erst als button programmiert sonst aber mit einer if abfrage der nfc welche lambda raise_frame(f2) verwendet
Button = tk.Button(f1, text="NFC einlesen",bg="white", command=lambda:raise_frame(f2)).place(relx=0.5,rely=0.7 ,anchor="center")

#Button um mit CP Zu bezahlen
Button1 = tk.Button(f2, text='-3',bg="white", command=lambda:raise_frame(f1), height=20, width=30).pack(side="left")
#Button um mit GP zu bezahlen
button2 = tk.Button(f2, text='-2', command=lambda:raise_frame(f1), height=20, width=30).pack(side="right")


raise_frame(f1)
Fullscreen(root)
root.mainloop()
