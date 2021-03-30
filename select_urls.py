# Given all the links from a query and the list of required programs,
# returns a csv file of just the required urls
# Written by Hiromichi Ueda '21 in January 2021
# 
# Last execution in macOS Big Sur in March 2021 
# with Python 3.8.3, Pandas 1.2.0
import pandas as pd

# parse url to get time and title of the program
def get_Time_and_Title(nds_url_str):
    prog_datetime = nds_url_str.split('&')[2].split('=')[-1]
    prog_title = nds_url_str.split('&')[4].split('=')[-1].replace('%20', ' ').replace('%40', '@')
    return prog_datetime[11:], prog_title

def select_urls(all_urls_file, programs_file):
    # df_prog has column names Date, Time, Title, Source, Market, URL, Scraped in this order   
    df_prog = pd.read_csv(programs_file)
    df_url = pd.read_csv(all_urls_file)
    # sort two dataframes in the same order
    for df in [df_prog, df_url]:
        df.sort_values(['Market', 'Source', 'Date', 'Time'], inplace=True, ignore_index=True)

    # insert missing time and title if one of them is missing
    df_missing = df_url.loc[df_url['Time'].isnull() | df_url['Title'].isnull()]
    for ind, row in df_missing.iterrows():
        prog_time, prog_title = get_Time_and_Title(row['URL'])
        df_url.loc[ind, 'Time'] = prog_time
        df_url.loc[ind, 'Title'] = prog_title

    df_prog['URL'] = ''

    search_start = 0
    for i in range(df_prog.shape[0]):
        ith_row_id = df_prog.loc[i, ['Date', 'Time', 'Title', 'Source', 'Market']].values 
        for j in range(df_url.shape[0]):
            jth_row_id = df_url.loc[j, ['Date', 'Time', 'Title', 'Source', 'Market']].values
            if all(ith_row_id == jth_row_id):
                df_prog.loc[i, 'URL'] = df_url.loc[j, 'URL'] #copy url
                break

    df_prog.to_csv(programs_file, index=False)
    df_url.to_csv(all_urls_file, index=False)