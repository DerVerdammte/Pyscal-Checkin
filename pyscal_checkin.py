
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
            auth_level = get_numpress("Auth Level Eingeben: 1 Member ",max=2,min=1)
        name = input("Benutzername Eingeben (Freiwillig): ")
        comment = input("Kommentar Hinzufügen (Freiwillig): ")

        body = auth_sheet.generate_body([second_nfc_id, member_nr, balance,
                                         auth_level,time.time(), name,
                                         comment], insert_time=True)
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

def admin_menu(first_index, first_row, auth_sheet):
    '''
    Opens up the Admin Menu for the Checkin System
    :param first_index: index in Spreadsheet of Admin
    :param first_row: row of Data of Admin
    :param auth_sheet: PyscalSheets object of Auth_Sheet
    :return: Log_Entry sting
    '''
    text = "1: Delete Other Card 2: Set Next Balance 3: Add Next Balance 4: Add New Profile"
    selection = int(get_numpress(text))
    print(selection)
    if selection == 1:
        print("Selected Deletion Option. Not yet implemented")
        #id, value, = reader.read()
        #log_message = 'Delete Operation - SecLvl 3: ' + delete_nfc_id(id,
        # value)
        log_message = "Wambo"
    elif selection ==2:
        log_message = "WIP Set some Balance"
    elif selection ==3:
        log_message = "WIP added Balace to Account"
    elif selection ==4:
        log_message = create_new_account(sec_level=3, auth_sheet=auth_sheet)


    elif selection ==5:
        log_message = "Create new Card for Existing Member"
    print(f"log message {log_message}")
    return log_message

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
                print("Mitarbeiter Menu: ")
                log_entry = log_entry + mitarbeiter_menu(first_index,
                                                         first_row,
                                              auth_sheet)
            elif sec_level == 3:
                log_entry = log_entry + admin_menu(first_index=first_index,
                                     first_row=first_row,
                           auth_sheet=auth_sheet)
            else:
                log_entry = log_entry + f"- [ERROR] Error in Sec-Level. " \
                                        f"Please " \
                                        f"contact System Admin"

    finally:
        GPIO.cleanup()
        print(f"Log Message: {log_entry}")
        body = auth_sheet.generate_body([nfc_id, log_entry], insert_time=True)
        auth_sheet.append_spreadsheet_row(body=body, is_log=True)

