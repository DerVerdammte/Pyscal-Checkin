from __future__ import print_function
import os.path
from googleapiclient import discovery
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import string

class Pyscalsheets:
    def __init__(self, spreadsheet_id, spreadsheet_log_id, empty_rows=0):
        '''
        Woop woop, ich weiß nicht was ich hier schreiben soll!
        :param spreadsheet_id: Id of main worksheet. This is the sheet where
        all commands are executed on normally.
        :param spreadsheet_log_id: Id of the Logfile Spreadsheet. Reccomended as you should always have a log file when using a cloud service.
        :param empty_rows: How many rows in the Main sheet are reserved for
        Descriptions / Text. This will offset the notion in the Program.
        '''
        self.set_spreadsheet_id(spreadsheet_id)
        self.set_log_spreadsheet_id(spreadsheet_log_id)
        self.empty_rows = empty_rows
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = discovery.build('sheets', 'v4', credentials=creds)

    def get_spreadsheet_id(self):
        return self.spreadsheet_id

    def set_spreadsheet_id(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    def get_log_spreadsheet_id(self):
        return self.log_spreadsheet_id

    def set_log_spreadsheet_id(self, log_spreadsheet_id):
        self.log_spreadsheet_id = log_spreadsheet_id

    def generate_body(self, array, insert_time = False):
        '''
        Creates the Payload for sending to the Google servers. Will add a
        time in the first row, if insert_time == True
        :param array: a value, 1D or 2D array.
        :param insert_time: Control if the first row will be generated with a timestamp.
        :return:
        '''
        values = []
        if insert_time:
            now = datetime.now()
            values.append(now.strftime("%d.%m.%y %H:%M:%S"))
        for i, element in enumerate(array):
            values.append(str(element))
        values = [values]
        return {'values':values}

    #def search_in_column(self):
    #
    #    return row

    def append_spreadsheet_row(self, body, range_ = 'A1:E1',
                               value_input_option = 'RAW',insert_data_option
                               = 'INSERT_ROWS', is_log = False):
        '''
        Adds a row to the spreadsheet using the append() command of the
        Google Sheet Api
        :param body: generated payload for the api. dont just press anything
        in here
        :param range_: optional - range of where to look for space before
        appending at the bottom/top
        :param value_input_option: optional - i have no clue
        :param insert_data_option: optional - "insert_rows" is what we want :D
        :param is_log: if is_log == true, we append the row to the
        log_spreadsheet instead of the other.
        :return: returns the answer to the request
        '''
        spreadsheet_id = self.get_spreadsheet_id()
        if is_log:
            spreadsheet_id = self.get_log_spreadsheet_id()
        request = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=body)
        return request.execute()

    def get_data_from_sheet(self, range_name = "A1:Z1000"):
        '''
        Retries all Date from table
        :param range_name: optional - Range of thing to be retrieved
        :return: array where each slice is one row of the sheet
        '''
        #Gets everything but the first row back from the Table. First row is
        # not copied to enable the user to label the rows.
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.get_spreadsheet_id(), range=range_name).execute()
        rows = result.get('values', [])
        #print('{0} rows retrieved.'.format(len(rows)))
        #for i,row in enumerate(rows):
        #    print(i,row)
        return rows[1:]

    def find_unique(self, key, key_index):
        '''
        returns the first item with 'key' in row[key]
        :param key: AnyType - Thing that is searched
        :param key_index: Int - Where it is being searched
        :return: index, row of the found search, else 0, None
        '''
        #INPUT: key and index of column in which to search. will only return
        # one item only use if you are sure that this is the only instance (unique)
        # of key in row.
        data = self.get_data_from_sheet()
        for i, row in enumerate(data):
            try:
                #print(f"compare {key} with {row[key_index]}")
                if str(row[key_index]) == str(key):
                    return i, row

            except TypeError:
                pass
        return -1, None

    def find_all_keys(self, key, key_index):
        '''
        Returns a list of all indices and rows that have the value 'key' in
        row[key_index].
        :param key: AnyType : Thing to be compared
        :param key_index: int int of the row that has to be placed.
        :return: Array, where every element is [index, row]
        '''
        #INPUT: key and index of column in which to search. will only return
        # one item only use if you are sure that this is the only instance (unique)
        # of key in row.
        data = self.get_data_from_sheet()
        return_array, element_count = [], 0
        for i, row in enumerate(data):
            try:
                if str(row[key_index]) == str(key):
                    return_array.append([i, row])
                    element_count = element_count+1
            except TypeError:
                print("AAAAAAAH")
        return element_count, return_array

    def delete_range(self, range_):
        '''
        Deletes a Range out of the Main Sheet
        :param range_: str - range to be deleted
        :return: Request answer from server
        '''
        #print("Delete Ranges Entered. Range:")
        #print(range_)
        request = self.service.spreadsheets().values().clear(
            spreadsheetId=self.get_spreadsheet_id(), range=range_)
        return request.execute()


    def convert_to_range(self, rf: int,rl: int, cf: int, cl: int, ro: int=0,
                         co: int=0)->str:
        '''
        @Arguments:
                rf (int): First Row
                rl (int): Last Row
                cf (int): First Column
                cl (int): Last Column
                ro (int): Row Offset
                co (int): Collumn Offset
        @Returns:
                The Range from the upper left cell
                to the down right cell in A1 notation

        '''
        #Beim berechnen der ranges müssen ggf oben ein paar zeilen
        # abgeschnitten werden.
        #print(f"ro: {ro} empty_rows: {self.empty_rows}")
        ro = ro + self.empty_rows +1

        return f"{string.ascii_uppercase[cf+co]}{rf+ro}:{string.ascii_uppercase[cl+co]}{rl+ro}"

    def replace_range(self, row_index, col_index, array):
        '''
        Replaces Area with information out of the array.
        :param row_index: index of row where the Replacement Starts
        :param col_index: index of col where the Replacement Starts
        :param array: NON JAGGED array.
        :return:
        '''
        rows = len(array)
        try:
            cols = len(array[0])
        except TypeError:
            cols = 1
        range = self.convert_to_range(row_index, row_index+rows-1, col_index,
                                      col_index+cols-1)
        #print("Range Calculated")
        #print(range)

        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.get_spreadsheet_id(), range=range,
            valueInputOption='RAW', body={'values':array}).execute()
        #print('{0} cells updated.'.format(result.get('updatedCells')))

    def delete_coords(self,row_first, row_last, col_first, col_last,
                      offset_row = 0, offset_col = 0):
        '''
        Deletes all the Things between the TopLeft and Bottom Right corner.
        :param row_first: First Row
        :param row_last: Last Row
        :param col_first: First Column
        :param col_last: Last Column
        :param offset_row: Offset Rows
        :param offset_col: Offset Columns
        :return: answer from server
        '''
        range_string = self.convert_to_range(rf=row_first,rl=row_last,
                                          cf=col_first,
                              cl=col_last, ro=offset_row, co=offset_col)
        return self.delete_range(range_string)

    def replace_field(self, row, col, value):
        '''
        Reolaces a single field in the main sheet with the value
        :param row: int. Index of the row you want to change
        :param col: int. index of the Column you want to change
        :param value: any - value to be placed in [row, column]
        :return: None (TODO: LOG FILE)
        '''
        self.replace_range(row_index=row, col_index=col, array=[value])

