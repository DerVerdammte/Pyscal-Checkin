import tkinter as tk
from PIL import Image, ImageTk
import time
import os
from FPTS import Fullscreen
from config import *


def load_screen(frame):
    frame.tkraise()


def pay(currency, amount):
    print(f"Payed {amount} {currency}")


def two_buttons(screen, links_text, rechts_text, links_kosten, rechts_kosten,
                links_wert,
                rechts_wert,
                links_farbe=COLOR_LEFT_BUTTON, rechts_farbe=COLOR_RIGHT_BUTTON):
    # Button um mit CP Zu bezahlen
    Button1 = tk.Button(screen, text=str(links_text), bg=links_farbe,
                        command=lambda: pay(currency="GP", amount=links_kosten),
                        height=20, width=30).place(relx=0.10, rely=0.5,
                                                   anchor="w")

    # Button um mit GP zu bezahlen
    button2 = tk.Button(screen, text='Pay with CP', command=lambda: pay(
        amount=3,
                                                                    currency="CP"),
                        height=20, width=30, bg=rechts_farbe).place(relx=0.90,
                                                   rely=0.5,
                                                   anchor="e")


if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

root = tk.Tk()

root.geometry("1280x900")
root.configure(bg=COLOR_BACKGROUND)
f1 = tk.Frame(root, bg=COLOR_BACKGROUND)
f2 = tk.Frame(root, bg=COLOR_BACKGROUND)

for frame in (f1, f2):
    frame.place(relheight=1, relwidth=1)

Logoimage = tk.PhotoImage(file=PATH_BACKGROUND)
background_label = tk.Label(f1, image=Logoimage).place(relwidth=1, relheight=1)
background_label2 = tk.Label(f2, image=Logoimage).place(relwidth=1, relheight=1)

label = tk.Label(f1, text="Bitte Nfc anlegen", fg="#9c3c30", bg="#131313",
                 font=("Arial",
                       20))  # hab fpr die farben die Hex Nr verwendet weil ich es durhc ein programm herrausgefunden hab alsou sollte passen
label.place(relx=0.5, rely=0.65, anchor="center")

Button = tk.Button(f1, text="NFC einlesen", bg="white",
                   command=lambda: load_screen(f2)).place(relx=0.5, rely=0.7,
                                                          anchor="center")

two_buttons(f2, links_text="Kosten in GP: 2", rechts_text="Kosten in CP: 3",
            links_kosten=2, rechts_kosten=3, links_wert=5, rechts_wert=9)

f1.tkraise()
Fullscreen(root)
root.mainloop()
