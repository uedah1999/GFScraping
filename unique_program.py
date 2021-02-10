# Given a xls file downloaded from News Data Service,
# returns unique broadcast as a csv file.
# Written by Hiromichi Ueda in January 2021
import pandas as pd

# convert "8:00 AM CT" to "08:00AM CT"
def format_time(time_str):
    if time_str[1] == ':':
        return_str = '0' + time_str
    else:
        return_str = time_str
    # convert "08:00 AM CT" to "08:00AM CT"
    return return_str[:5] + return_str[6:]

def get_unique_program(nds_xls, programs_file):
    programs = pd.read_excel(nds_xls)
    program_uni = programs.loc[:, ['Date', 'Time', 'Title', 'Source', 'Market']].drop_duplicates()
    df = program_uni.assign(Date = pd.to_datetime(program_uni['Date'], format='%b %d %Y')).astype(str)
    df['Time'] = df['Time'].apply(format_time)
    df_sorted = df.sort_values(['Market', 'Source', 'Date', 'Time'])
    df_sorted.reset_index(drop=True, inplace=True)
    df_sorted.to_csv(programs_file, index=False)