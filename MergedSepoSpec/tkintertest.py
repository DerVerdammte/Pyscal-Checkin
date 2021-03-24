import tkinter as tk
from PIL import Image, ImageTk
import time
import os
from FPTS import Fullscreen
from config import *
import pyscal_checkin as pc
from mfrc522 import SimpleMFRC522
from pyscal_gui import *


def load_screen(frame):
    frame.tkraise()


def pay(currency, amount):
    print(f"Payed {amount} {currency}")


def two_buttons(frame, links_text, rechts_text, links_kosten, rechts_kosten,
                links_wert,
                rechts_wert,
                links_farbe=COLOR_LEFT_BUTTON, rechts_farbe=COLOR_RIGHT_BUTTON):
    # Clear Frame
    clear_frame(input_frame=frame)

    # Button um mit CP Zu bezahlen
    button1 = tk.Button(frame, text=str(links_text), bg=links_farbe,
                        command=lambda: pay(currency="GP", amount=links_kosten),
                        height=20, width=30).place(relx=0.10, rely=0.5,
                                                   anchor="w")

    # Button um mit GP zu bezahlen
    button2 = tk.Button(frame, text='Pay with CP', command=lambda: pay(
        amount=3, currency="CP"),
                        height=20, width=30, bg=rechts_farbe).place(relx=0.90,
                                                                    rely=0.5,
                                                                    anchor="e")
    # Make the Frame Visible
    frame.tkraise()


def clear_frame(input_frame):
    # destroy all widgets from frame
    for widget in input_frame.winfo_children():
        widget.destroy()

    # this will clear frame and frame will be empty
    # if you want to hide the empty panel then
    input_frame.pack_forget()


def scan_nfc(reader_):
    '''
    Scans the NFC Tag
    :param reader_: Reading object of the SimpleMFRC522 Library
    :return: id, Values stored on Chip
    '''
    print("NFC SCANNER ACTIVE")
    answer = reader_.read()
    print(answer)
    return answer


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
                       20))  # hab fpr die farben die Hex Nr verwendet weil
# ich es durhc ein programm herrausgefunden hab alsou sollte passen
label.place(relx=0.5, rely=0.65, anchor="center")

# Button = tk.Button(f1, text="NFC einlesen", bg="white",
#                   command=lambda: load_screen(f2)).place(relx=0.5, rely=0.7,
#                                                          anchor="center")

reader = SimpleMFRC522()
Button = tk.Button(f1, text="NFC einlesen", bg="white",
                   command=lambda: scan_nfc(reader_=reader)).place(relx=0.5,
                                                                   rely=0.7,
                                                                   anchor="center")

two_buttons(f2, links_text="Kosten in GP: 2", rechts_text="Kosten in CP: 3",
            links_kosten=2, rechts_kosten=3, links_wert=5, rechts_wert=9)

f1.tkraise()
Fullscreen(root)
root.mainloop()
