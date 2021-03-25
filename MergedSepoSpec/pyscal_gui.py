import os
import tkinter as tk

import mpimg as mpimg

from FPTS import Fullscreen
from mfrc522 import SimpleMFRC522
import pyscal_checkin as pc
from PIL import Image, ImageTk
from config import *
import Pyscal as ps
from PIL import Image
from IPython.display import display, Image


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
        self.pyscal_sheets = ps.Pyscalsheets(
            "1ZhVw2du5qQ_oBQdTN4FXLfDZCgR95o7IbCGDstekrCc",
            "1NG-Avb1WymSAfApRnCK6BIwevV_ssn187WqEbvFLU7c",
            1)  ##Pyscal
        # save tkinter_root
        self.tkinter_root = tk.Tk()
        self.tkinter_root.geometry("1280x800")
        # self.tkinter_root.configure(bg="black") #COLOR_BACKGROUND
        self.frame_welcome = None
        self.frame_wellness_entrance = None
        self.create_welcome()

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
        self.member_id, self.current_user_array = \
            self.pyscal_sheets.find_unique(id,
                                                               AUTH_LABELS[
                                                                   "nfc_id"])
        print(f"Member ID: {self.member_id} data_Array: {self.current_user_array}")
        links_text = STRING_LINKER_TEXT_WELLNESS
        rechts_text = STRING_RECHTER_TEXT_WELLNESS
        links_kosten = KOSTEN_WELLNESS_GP
        rechts_kosten = KOSTEN_WELLNESS_CP
        links_wert = self.current_user_array[AUTH_LABELS["balance"]]
        rechts_wert = self.current_user_array[AUTH_LABELS["corona_points"]]
        self.draw_pay_page(self.frame_wellness_entrance, links_text=links_text,
                           rechts_text=rechts_text, rechts_wert=rechts_wert,
                           rechts_kosten=rechts_kosten, links_kosten=links_kosten, links_wert=links_wert)

    def set_current_user(self, user_data_array):
        self.current_user = user_data_array

    def get_current_user(self):
        return self.current_user

    def set_current_nfc_id(self, nfc_id):
        self.current_nfc_id = nfc_id

    def get_current_nfc_id(self):
        return self.current_nfc_id


    def draw_pay_page(self, frame, links_text, rechts_text, links_kosten,
                      rechts_kosten, links_wert, rechts_wert,
                      links_farbe=COLOR_LEFT_BUTTON,
                      rechts_farbe=COLOR_RIGHT_BUTTON):
        # Clear Frame
        clear_frame(input_frame=frame)

        logo_image = tk.PhotoImage(file="Logo3.gif")
        background_label = tk.Label(self.frame_wellness_entrance, image=logo_image)
        background_label.photo = logo_image
        background_label.place(relwidth=1, relheight=1)

        # Button um mit CP Zu bezahlen
        button1 = tk.Button(frame, text=str(links_text), bg=links_farbe,
                            command=lambda: self.user_pay(currency="GP",
                                                          amount=links_kosten),
                            height=20, width=30).place(relx=0.10, rely=0.5,
                                                       anchor="w")

        # Button um mit GP zu bezahlen
        button2 = tk.Button(frame, text=str(rechts_text), command=lambda:
            self.user_pay(currency="CP", amount=rechts_kosten), height=20,
                            width=30,
                            bg=rechts_farbe).place(relx=0.90, rely=0.5,
                                                   anchor="e")

        # Make the Frame Visible
        frame.tkraise()

    def user_pay(self, currency="GP", amount=1):
        amount = int(amount)
        auth_sheet = self.pyscal_sheets
        member_number = self.current_user_array[AUTH_LABELS["member_id"]]
        if currency == "GP":
            old_balance = self.current_user_array[AUTH_LABELS["balance"]]
        if currency == "CP":
            old_balance = self.current_user_array[AUTH_LABELS["corona_points"]]
        self.frame_welcome.tkraise()
        pc.user_pay(self.member_id, auth_sheet, old_balance,member_number ,
                    price=amount, currency=currency)
        #self.scan_for_nfc()

    def create_welcome(self):
        self.frame_welcome = tk.Frame(
            self.tkinter_root)  # , bg=COLOR_BACKGROUND
        self.frame_welcome.place(relheight=1, relwidth=1)

        self.frame_wellness_entrance = tk.Frame(self.tkinter_root)
        self.frame_wellness_entrance.place(relheight=1, relwidth=1)

        # Codeabschnitt 1: Hintergrund Laden
        logo_image = tk.PhotoImage(file="Logo2.gif")
        background_label = tk.Label(self.frame_welcome, image=logo_image)
        background_label.photo = logo_image
        background_label.place(relwidth=1, relheight=1)

        # Codeabschnitt 2: Texbox Laden
        # nfc_prompt = tk.Label(self.frame_welcome, text="Bitte Nfc anlegen",
        # fg="#9c3c30",
        #                bg="#131313", font=("Arial", 20))
        # nfc_prompt.place(relx=0.5, rely=0.70, anchor="center")

        button = tk.Button(self.frame_welcome, text="Aktivieren", bg="white",
                           command=lambda: self.scan_for_nfc())
        button.place(relx=0.5, rely=0.9,
                     anchor="center")

        self.frame_welcome.tkraise()


print("Attempting Logo")
display(Image(filename='Logo2.gif'))

gui = PyscalGui()

Fullscreen(gui.tkinter_root)
gui.tkinter_root.mainloop()
