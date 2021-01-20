# Given all the links from a query and the list of required programs,
# returns a csv file of just the required urls
# Written by Hiromichi Ueda in January 2021
import pandas as pd
import csv

all_urls_file = '../Data/{}_url_all.csv'.format(station_name)
file_all_links = '../Data/{}_programs.csv'.format(station_name) #change it to your file
file_prog_links = '../Data/{}_url_programs.csv'.format(station_name)

