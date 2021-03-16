
from __future__ import print_function
import Pyscal as ps
from config import *
from mfrc522 import SimpleMFRC522
import time

import RPi.GPIO as GPIO
#from pprint import pprint

#from googleapiclient import discovery
#import pickle
#import os.path
#from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request
#from datetime import datetime

def get_numpress(description = "" ,min = 0, max = 9, default = 0):
    print(description)
    print(f"Press Button between {min} and {max}")
    while True:
        ans = input("Press Selection")
        try:
            ans = int(ans)
        except ValueError:
            print(f"Cant Convert {ans} to Int")
            ans = -1

        print(f"Ans is {ans}, min is {min} and max is {max}")
        if (int(ans) >= int(min) and int(ans) <= int(max)):
            return ans
        else:
            print(f"Invalid Answer: ans = {ans} is out of bounds. Try Again")

def scan_nfc(reader_):
    '''
    Scans the NFC Tag
    :param reader_: Reading object of the SimpleMFRC522 Library
    :return: id, Values stored on Chip
    '''
    return reader_.read()

def create_new_account(sec_level, auth_sheet):
    '''
    Opens up the new user Generation menu.
    :param sec_level: Sec level of the person that is issuing the card. 2
    Worker, 3 Admin
    :param auth_sheet: Pyscalsheet Object of the Auth_Sheet you want to Change
    :return: Log Message (String)
    '''
    print("Present the new Card")
    second_nfc_id, nfc_payload = reader.read()
    second_index, second_row = auth_sheet.find_unique(second_nfc_id,
                                                      AUTH_LABELS["nfc_id"])
    if second_index is -1:
        #member nummer
        member_nr = get_numpress("Mitgliedsnummer aus dem Athletics System: ",
                                 max=99999999, min=1)
        balance = get_numpress("Startguthaben des Mitgliedes eingeben:  ",
                               max=10000, min=0)
        if sec_level == 3:
            auth_level = get_numpress("Auth Level Eingeben: 1 Member, 2 Mitarbeiter, 3 Admin ",max=3,min=1)
        else:
            auth_level = 1  #= get_numpress("Auth Level Eingeben: 1 Member ",max=2,min=1)
        name = input("Benutzername Eingeben (Freiwillig): ")
        corona_shakes = get_numpress("Euro Guthaben Eingeben (Max 100) ", max=100, min=0)
        euro_balance = get_numpress("Anzahl Corona-Punkte: ", max=50, min=0)
        comment = input("Kommentar Hinzufügen (Freiwillig): ")

        body = auth_sheet.generate_body([second_nfc_id, member_nr, balance,
                                         auth_level,time.time(), name,
                                         comment, euro_balance, corona_shakes], insert_time=True)
        auth_sheet.append_spreadsheet_row(body)
        return f"Generated new Account with stats: {body}"
    else:
        return "Card Already Registered"


def user_pay(id, auth_sheet, old_balance, member_id, price = ENTRY_PRICE):
    '''
    Changes the Entry of the Money in the User indicated by the excel row (id).

    :param id: Rownumber in the Spreadsheet of Customer.
    :param auth_sheet: Pyscalsheets object of User Data
    :param old_balance: Old Value of Balance
    :param member_id: Member ID for generating a better log entry
    :param price: Standard 1, may change.
    :return: Returns a String of Log Entry
    '''
    auth_sheet.replace_field(row=id, col=AUTH_LABELS["balance"],
                             value=[int(old_balance)-price])
    auth_sheet.replace_field(row=id, col=AUTH_LABELS["timestamp_last"],
                             value=[int(time.time())])
    balance = int(old_balance)-price
    return f"User {member_id} has Paid {price} points for entry. {balance} " \
           f"Points left"

def open_door():
    print("Door Opened")
    time.sleep(1)
    print("Dorr Closed")

def admin_menu(first_index, first_row, auth_sheet):
    '''
    Opens up the Admin Menu for the Checkin System
    :param first_index: index in Spreadsheet of Admin
    :param first_row: row of Data of Admin
    :param auth_sheet: PyscalSheets object of Auth_Sheet
    :return: Log_Entry sting
    '''
    text = "\nADMIN MENU: \n1: Enter Area \n2: Add New Profile \n3: Delete Other " \
           "Card \n4: Add Wellness_Points to Card. \n5: Add Euro-Points to card.\n6:Add Corona-Points to card\n7: Add new Card to Existing Member"
    selection = int(get_numpress(text))
    print(selection)


    if selection ==1:
        #Enter the Area
        open_door()
        log_message = "Enter Area"
    elif selection == 2:
        #Add new Profile
        log_message = create_new_account(sec_level=3, auth_sheet=auth_sheet)
    elif selection ==3:
        #Delete Profile
        print("Selected Deletion Option. Not yet implemented")
        id, value, = reader.read()
        log_message = delete_nfc_id(id, auth_sheet)
    #elif selection ==4:
    #    #Set Balance of Other Card
    #    log_message = set_balance(auth_sheet=auth_sheet)
    elif selection ==4:
        log_message = add_balance(auth_sheet=auth_sheet, balance_index=AUTH_LABELS["balance"])
    elif selection ==5:
        log_message = add_balance(auth_sheet=auth_sheet, balance_index=AUTH_LABELS["euro_balance"])
    elif selection ==6:
        log_message = add_balance(auth_sheet=auth_sheet, balance_index=AUTH_LABELS["corona_points"])
    elif selection ==7:
        log_message = "Assign New NFC-Card to Athletics Member_ID"

    print(f"log message {log_message}")
    return log_message

def set_balance(auth_sheet):
    print("Present the new Card")
    second_nfc_id, nfc_payload = reader.read()
    second_index, second_row = auth_sheet.find_unique(second_nfc_id,
                                                      AUTH_LABELS["nfc_id"])
    balance = get_numpress("Neues Guthaben des Kunden:  ",
                           max=10000, min=0)
    second_row[AUTH_LABELS["balance"]] = balance
    auth_sheet.replace_range(second_index, 0, [second_row])

def add_balance(auth_sheet, balance_index):
    print("Present the new Card")
    second_nfc_id, nfc_payload = reader.read()
    second_index, second_row = auth_sheet.find_unique(second_nfc_id,
                                                      AUTH_LABELS["nfc_id"])
    balance = int(get_numpress("Guthaben des Kunden erhöhen um: ",
                           max=10000, min=0)) + int(second_row[balance_index])
    second_row[balance_index] = balance
    auth_sheet.replace_range(second_index, 0, [second_row])
    mitglieds_id = second_row[AUTH_LABELS["member_id"]]
    return f"Guthaben des Kunden {mitglieds_id} um {balance} erhöht. "

def delete_nfc_id(id, auth_sheet):
    second_id, second_row = auth_sheet.find_unique(id, AUTH_LABELS["nfc_id"])
    member_id = second_row[AUTH_LABELS["member_id"]]
    second_row[AUTH_LABELS["comment"]] = "Old Member ID: "+ second_row[
        AUTH_LABELS["member_id"]] + second_row[AUTH_LABELS["comment"]]
    second_row[AUTH_LABELS["nfc_id"]], second_row[AUTH_LABELS["member_id"]] = \
        "",""
    auth_sheet.replace_range(second_id, 0, [second_row])
    return f"Deleted user {member_id} with NFC_ID {id}, "


def mitarbeiter_menu(first_index, first_row, auth_sheet):
    '''
    Opens up the Menu for the Workers. Should not enable Delete operation for Data Protection Reasons and stuff.
    :param first_index: Index in Spreadsheet of Worker
    :param first_row: Row of the Worker
    :param auth_sheet: Pyscalsheets object of the Auth_Sheet
    :return: log message
    '''
    text = "1: Enter 2: Add New Profile"
    selection = int(get_numpress(text,1,2))
    print(selection)
    if selection ==1:
        log_message = "Door Open, Worker"
    elif selection ==2:
        log_message = create_new_account(2, auth_sheet=auth_sheet)
    return log_message

def kassenfunktion():
    nfc_id, value = scan_nfc(reader)
    log_entry = ""
    first_index, first_row = auth_sheet.find_unique(nfc_id, AUTH_LABELS[
        "nfc_id"])
    try:
        euro_balance, corona_balance = int(first_row[AUTH_LABELS["euro_balance"]]), int(first_row[AUTH_LABELS["corona_points"]])
    except TypeError:
        print("User not Registered")
        return "Transaction Did not work"
    except IndexError:
        print("Index Error")
        return "Transaction Did not Work"
    selection = int(get_numpress(f"Mit Points oder Corona_Points zahlen?\n1) Points {euro_balance}\n2)Corona Points {corona_balance} ",
                               max=2, min=1))
    amount = int(get_numpress(f"Betrag eingeben:\n",
        max=100, min=0))

    if selection == 1:
        #bezahlen mit normalen_punkten
        if amount <= euro_balance:
            #zu viel
            first_row[AUTH_LABELS["euro_balance"]] = euro_balance-amount
            auth_sheet.replace_range(first_index, 0, [first_row])
            log_entry = f"User paid {amount} Gym-Points, they have {euro_balance-amount} Gym-Points left"
        else:
            #möglich
            log_entry = "User has not enough money left"
    if selection == 2:
        #bezahlen mit corona_punkten

        if amount <= corona_balance:
            #möglich
            first_row[AUTH_LABELS["corona_points"]] = corona_balance - amount
            auth_sheet.replace_range(first_index, 0, [first_row])
            log_entry = f"User paid {amount} Corona-Points, they have {corona_balance - amount} Corona-Points left"
        else:
            #nicht möglich
            log_entry = "User has not enough Corona-Points left."

    return log_entry

auth_sheet = ps.Pyscalsheets("1ZhVw2du5qQ_oBQdTN4FXLfDZCgR95o7IbCGDstekrCc",
                      "1NG-Avb1WymSAfApRnCK6BIwevV_ssn187WqEbvFLU7c",
                      1) ##Pyscal
reader = SimpleMFRC522()

#create_new_account(3, auth_sheet=auth_sheet)
print("Present your ID")
while True:
    time.sleep(1)
    try:
        nfc_id, value = scan_nfc(reader)
        log_entry = ""
        first_index, first_row = auth_sheet.find_unique(nfc_id, AUTH_LABELS[
            "nfc_id"])
        #Hier passe ich die kassenkarte ab, um die kassenfeatures zu testen
        if int(nfc_id) == 520580871409:
            print("KASSE BIS ZUM NÄCHSTEN RESTART AKTIVIERT!")
            while True:
                print("Present NFC Tag of Customer")
                print(kassenfunktion())

        #print(f"first_index: {first_index}, first row: {first_row}")
        if first_index == -1:
            log_entry = log_entry + " [ERROR] NFC Chip not registered"
        else:
            sec_level = int(first_row[AUTH_LABELS["security_level"]])
            log_entry = log_entry + f"SecLvl{sec_level} "

            if sec_level == 1:
                #ID card Belongs to normal User. Check for Balance and Last
                # Checkin
                temp_time = int(first_row[AUTH_LABELS["timestamp_last"]][0:10])
                curr_time = int(str(time.time())[0:10])
                difference = curr_time-temp_time
                #print(f"Start time {temp_time}, End Time {curr_time}, diff = "
                #   f"{difference}")
                #print(f"difference: {difference} CHECKIN_COOLDOWN:
                # {CHECKIN_COOLDOWN}")
                if difference > CHECKIN_COOLDOWN:
                    #cooldown has already passed
                    if int(first_row[AUTH_LABELS["balance"]]) >= 1:
                        #user has enough money and his cooldown passed
                        log_entry = log_entry + user_pay(first_index, auth_sheet, first_row[
                            AUTH_LABELS["balance"]], first_row[AUTH_LABELS[
                            "member_id"]])

                    else:
                        #user has not enough money.
                        log_entry = log_entry + "Access Denied. User has no " \
                                              "more Tokens"
                else:
                    #user was logged in a few moments ago, no money deducted
                    log_entry = log_entry + "User war erst Eingeloggt. Kein " \
                                          "Geld Abgezogen"
            elif sec_level == 2:
                #user is worker
                print("Mitarbeiter Menu: ")
                log_entry = log_entry + mitarbeiter_menu(first_index,
                                                         first_row,
                                              auth_sheet)
            elif sec_level == 3:
                #user is Administrator
                log_entry = log_entry + str(admin_menu(first_index=first_index,
                                     first_row=first_row,
                           auth_sheet=auth_sheet))
            else:
                log_entry = log_entry + f"- [ERROR] Error in Sec-Level. " \
                                        f"Please " \
                                        f"contact System Admin"



    finally:
        GPIO.cleanup()
        print(f"Log Message: {log_entry}")
        body = auth_sheet.generate_body([nfc_id, log_entry], insert_time=True)
        auth_sheet.append_spreadsheet_row(body=body, is_log=True)
        print("Please Present your ID")

