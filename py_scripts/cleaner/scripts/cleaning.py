import pandas as pd
from key_finder import get_keys_of_interest

def get_years(path):
    df = pd.read_excel(path)
    years = df.iloc[11].tolist()[1:]
    for i in range(len(years)):
        years[i] = years[i][3:]
    return years #output is a list of strings

def format_raw_df(path):
    df = pd.read_excel(path)
    new_df = df.transpose()
    new_df.columns = new_df.iloc[0]
    new_df = new_df[1:]
    #print(new_df)
    return new_df

def sub_df(df_path,keys):
    df = format_raw_df(df_path)
    new_df = df[keys]
    return new_df

def make_dict(df_path,keys):
    subdf = sub_df(df_path,keys)
    years = get_years(df_path)
    #print(clean_df.shape)
    #print(clean_df)
    dict_out = {}
    for indicator in subdf.columns.values:
        temp_dic = {}
        for i in range(len(years)):
            temp_dic[years[i]]= subdf[indicator].iloc[i]
        dict_out[indicator] = temp_dic
    return dict_out
