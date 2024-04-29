from extract_jsons import get_jsons_ls
import pandas as pd
import json
import os 
def read_json_data(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    # Initialize an empty DataFrame
    df_final = pd.DataFrame()
    
    # Loop through each metric in the JSON
    for metric, yearly_data in data.items():
        # Convert yearly data to DataFrame
        df_temp = pd.DataFrame(list(yearly_data.items()), columns=['Financial Year', metric])
        
        if df_final.empty:
            df_final = df_temp
        else:
            # Merge the temporary DataFrame with the final DataFrame on 'Year'
            df_final = pd.merge(df_final, df_temp, on='Financial Year')
    
    # Add the company name as a new column (assuming the company name is known)
    company_name = json_path.split('\\')[-1]
    df_final['Peer'] = company_name
    
    # Reorder DataFrame columns to match the desired output
    column_order = ['Peer', 'Financial Year', 'Total Revenue', 'EBITDA', 'EBITDA Margin', 'Basic EPS']
    df_final = df_final[column_order]
    return df_final

def merge_jsons():
    dfs = []  # List to store each DataFrame
    json_ls = get_jsons_ls()
    for file_path in json_ls:
        # Convert each JSON file to a DataFrame
        df =read_json_data(file_path)
        dfs.append(df)
    
    # Combine all DataFrames in the list into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.sort_values(by=['Financial Year'], ascending=False, inplace=True)
    
    return combined_df

def df_to_csv(df):
    csv_file_path = 'combined_data.csv'  # Update this path as needed

    # Save the DataFrame to CSV
    df.to_csv(csv_file_path, index=False)

print(merge_jsons())
