import pandas as pd
data1 = {
    "Company Name": ["SIA Group", "SIA Group", "SIA", "SIA", "SIA", "SIA", "SIA", "SIA", "SIA", "SIA", "SIA", "SIA", "SilkAir", "SilkAir"],
    "Financial_Year": [2023, 2022, 2018, 2017, 2019, 2018, 2021, 2020, 2021, 2020, 2021, 2020, 2021, 2020],
    "Passenger Load Factor (%)": [85.4, 39.6, 81.1, 79.0, 83.1, 81.1, 13.4, 81.9, 12.5, 79.1, 13.7, 81.5, 12.5, 80.0]
}
data2 = {
    "Company Name": ["SIA Group", "SIA", "Scoot", "SIA Group", "Parent Airline Company", "SilkAir", "Scoot", "SIA Cargo", "SIA Engineering", "Parent Airline Company", "SilkAir", "Scoot", "SIA Engineering", "SIA Group", "SIA Group"],
    "Financial_Year": [2023, 2023, 2023, 2022, 2018, 2018, 2018, 2018, 2018, 2019, 2019, 2019, 2019, 2020, 2021],
    "Operating Profit (Millions)": ["2,692", "2,601", "148", "10", "137", "3", "29", "28", "20", "204", "11", "-6", "19", "59.1", "-2,512.5"]
}

def prefer_sia_group(group):
    if 'SIA Group' in group['Company Name'].values:
        return group[group['Company Name'] == 'SIA Group']
    return group 

def max_value_with_metadata(series):
    return max(series, key=lambda x: x.value)

def remove_SIA(df, metric):
    # Replace 'SIA' with 'SIA Group' in the Company Name column
    df['Company Name'] = df['Company Name'].replace('SIA', 'SIA Group')
    
    # Use custom aggregation to work with Value_With_Metadata objects
    df = df.groupby(['Company Name', 'Financial_Year'], as_index=False).agg({metric: max_value_with_metadata})
    
    return df
    
def cleanup_df(df):
    metric = df.columns.values[-1]
    print(metric)
    # Filter for 'SIA Group' or 'SIA'
    df_filtered = df[df["Company Name"].isin(["SIA Group", "SIA"])]
    df_preferred = df_filtered.groupby('Financial_Year').apply(prefer_sia_group).reset_index(drop=True)
    df_final = remove_SIA(df_preferred,metric)
    return df_final

def select_years(df,start_year,end_year):
    filtered_df = df[(df['Financial_Year'] >= start_year) & (df['Financial_Year'] <= end_year)]
    return filtered_df