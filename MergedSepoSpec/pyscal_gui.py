import os
import tkinter as tk
from FPTS import Fullscreen
from mfrc522 import SimpleMFRC522

from config import *
import Pyscal as ps


def clear_frame(input_frame):
    # destroy all widgets from frame
    for widget in input_frame.winfo_children():
        widget.destroy()

    # this will clear frame and frame will be empty
    # if you want to hide the empty panel then
    input_frame.pack_forget()


def load_screen(frame):
    frame.tkraise()

class PyscalGui:
    def __init__(self):
        if os.environ.get('DISPLAY', '') == '':
            print('no display found. Using :0.0')
            os.environ.__setitem__('DISPLAY', ':0.0')


    # initialize NFC-Reader
        self.reader = SimpleMFRC522()
        # save pyscal_sheets_object
        self.pyscal_sheets = ps.Pyscalsheets("1ZhVw2du5qQ_oBQdTN4FXLfDZCgR95o7IbCGDstekrCc",
                                              "1NG-Avb1WymSAfApRnCK6BIwevV_ssn187WqEbvFLU7c",
                                              1) ##Pyscal
        # save tkinter_root
        self.tkinter_root = tk.Tk()
        self.tkinter_root.geometry("1280x900")
        self.tkinter_root.configure(bg=COLOR_BACKGROUND)
        self.frame_welcome = self.create_welcome()

        self.current_user_array = []
        self.current_nfc_id = 0

    # def create_frame(self):
    #    new_frame = tk.Frame(self.tkinter_root, bg=COLOR_BACKGROUND)
    #    self.frame_list.append(new_frame)
    #    return self.frame_list[-1]

    def scan_for_nfc(self):
        ''''''
        print("NFC SCANNER ACTIVE")
        id, value = self.reader.read()
        self.set_current_nfc_id(nfc_id=id)
        member_id, data_array = self.pyscal_sheets.find_unique(id,
                                                          AUTH_LABELS["nfc_id"])
        print(f"Member ID: {member_id} data_Array: {data_array}")

    def set_current_user(self, user_data_array):
        self.current_user = user_data_array

    def get_current_user(self):
        return self.current_user

    def set_current_nfc_id(self, nfc_id):
        self.current_nfc_id = nfc_id

    def get_current_nfc_id(self):
        return self.current_nfc_id

    def user_pay(self, currency, amount):
        print(f"User Pay currency: {currency} amount: {amount}")
        print(f"User: {self.current_user_array}")

    def draw_pay_page(self, frame, links_text, rechts_text, links_kosten,
                    rechts_kosten, links_wert,rechts_wert,
                    links_farbe=COLOR_LEFT_BUTTON,
                    rechts_farbe=COLOR_RIGHT_BUTTON):
        # Clear Frame
        clear_frame(input_frame=frame)

        # Button um mit CP Zu bezahlen
        button1 = tk.Button(frame, text=str(links_text), bg=links_farbe,
                            command=lambda: self.user_pay(currency="GP",
                                              amount=links_kosten),
                            height=20, width=30).place(relx=0.10, rely=0.5,
                                                       anchor="w")

        frame.tkraise()
        # Button um mit GP zu bezahlen
        button2 = tk.Button(frame, text='Pay with CP', command=lambda:
                            self.user_pay(currency="GP",amount=links_kosten),
                            height=20, width=30,
                            bg=rechts_farbe).place(relx=0.90,  rely=0.5,
                                                   anchor="e")

        # Make the Frame Visible
        frame.tkraise()



    def create_welcome(self):
        frame_ = tk.Frame(self.tkinter_root, bg=COLOR_BACKGROUND)
        frame_.place(relheight=1, relwidth=1)

        # Codeabschnitt 1: Hintergrund Laden
        logo_image = tk.PhotoImage(file=PATH_BACKGROUND)
        background_label = tk.Label(frame_, image=logo_image)
        background_label.place(relwidth=1,relheight=1)
        frame_.tkraise()
        # Codeabschnitt 2: Texbox Laden
        nfc_prompt = tk.Label(frame_, text="Bitte Nfc anlegen", fg="#9c3c30",
                        bg="#131313", font=("Arial", 20))
        nfc_prompt.place(relx=0.5, rely=0.65, anchor="center")

        frame_.tkraise()
        #self.scan_for_nfc()


gui = PyscalGui()
gui.create_welcome()

Fullscreen(gui.tkinter_root)
gui.tkinter_root.mainloop()


