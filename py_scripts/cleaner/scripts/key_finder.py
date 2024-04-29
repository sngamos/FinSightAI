
import pandas as pd
def get_keys_of_interest(keys_ls = None,csv_path=None):
    keys_ls_out =[]
    if keys_ls == None:
        stop = False
        keys_ls = []
        while stop == False:
            user_in = input('Input financial indicator of interest.\nPress Enter when done.\nIndicator: ')
            if user_in == "":
                stop = True
            else:
                if check_valid_key(user_in,get_csv_keys(csv_path)) != None:
                    keys_ls_out.append(user_in)
    else:
        for i in keys_ls:
            #print(i)
            if check_valid_key(i,get_csv_keys(csv_path)) != None:
                keys_ls_out.append(i)
    if len(keys_ls_out) == 0:
        print('There is nothing in your list of keys')
        return None
    else: 
        return keys_ls_out
        
def check_valid_key(key,csv_keys):
    if key in csv_keys:
        return key
    else:
        print(f'\n=========================================================\nERROR: <{key}> is not a valid list in excel sheet\nWill ignore and proceed for now\nPLEASE FIX ASAP AND RETRY\n=========================================================\n')
        return None


def get_csv_keys(csv_path=None):
    df = pd.read_excel(csv_path).transpose()
    df.columns = df.iloc[0]
    df = df[1:]
    key_list = df.columns.values
    return key_list

#check_valid_key('EBITDA Margin',get_csv_keys('C:\\Users\\sngam\\SUTD\\TemasekxSUTD\\genai-starter-kit\\cleaner\\csv_dump\\Amazon.xls'))



