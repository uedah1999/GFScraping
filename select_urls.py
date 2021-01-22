# Given all the links from a query and the list of required programs,
# returns a csv file of just the required urls
# Written by Hiromichi Ueda in January 2021
import numpy as np
import pandas as pd
import csv

def get_Time_and_Title(nds_url_str):
    prog_datetime = nds_url_str.split('&')[2].split('=')[-1]
    prog_title = nds_url_str.split('&')[4].split('=')[-1].replace('%20', ' ')
    return prog_datetime[11:], prog_title

station_name = 'KMSP'

all_urls_file = '../GFData/{}_url_all.csv'.format(station_name)
programs_file = '../GFData/{}_programs.csv'.format(station_name) #change it to your file
programs_url_links = '../GFData/{}_url_programs.csv'.format(station_name)

df_prog = pd.read_csv(programs_file, index_col=0)
df_url = pd.read_csv(all_urls_file, header=None)
df_missing = df_url.loc[df_url[1].isnull() & df_url[5].notnull()]
for ind, row in df_missing.iterrows():
    prog_time, prog_title = get_Time_and_Title(row[5])
    df_url.loc[ind, 1] = prog_time
    df_url.loc[ind, 2] = prog_title

df_prog['URL'] = np.nan

search_start = 0
for i in range(df_prog.shape[0]):
    ith_row_id = df_prog.iloc[i,:5].values 
    j = search_start
    while j < df_url.shape[0]:
        jth_row_id = df_url.iloc[j,:5].values
        if all(ith_row_id == jth_row_id):
            df_prog.iloc[i,-1] = df_url.iloc[j,-1]
            search_start = j+1
            break
        else:
            j += 1

df_prog['Scraped'] = False
df_prog.to_csv(programs_url_links)