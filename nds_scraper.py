# This file is used to iterate through each url,
# scrape the text within the url, and store it in the directory we want.
# Written by Nobuaki Masaki in June 2019
# Revised by Xinyan Xiang in July 2020
# Revised by Hiromichi Ueda in January 2021

import pandas as pd
import os

station_name = 'WCCO'

# imports the file with links
programs_url_links = '../GFData/{}_url_programs.csv'.format(station_name)
programs = pd.read_csv(programs_url_links)
df = pd.read_csv(programs_url_links, index_col=0)

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# options to make webdriver run in the background
op = Options()
op.add_argument("--disable-gpu");
op.add_argument("--disable-extensions");
op.add_argument("--proxy-server='direct://'");
op.add_argument("--proxy-bypass-list=*");
op.add_argument("--start-maximized");
op.add_argument("--headless");

driver = webdriver.Chrome(options=op)

# this function formats the date so that it can be used for directory names
def return_Date_str(Date):

    monthToNum = {
        'JAN' : '1',
        'FEB' : '2',
        'MAR' : '3',
        'APR' : '4',
        'MAY' : '5',
        'JUN' : '6',
        'JUL' : '7',
        'AUG' : '8',
        'SEP' : '9',
        'OCT' : '10',
        'NOV' : '11',
        'DEC' : '12'
    }

    parse_date = Date.split(" ")

    month = monthToNum[parse_date[0]]
    date = parse_date[1]
    year = parse_date[2]

    return year + "-" + month + "-" + date, month
def year_get(Date):
    monthToNum = {
        'JAN' : '1',
        'FEB' : '2',
        'MAR' : '3',
        'APR' : '4',
        'MAY' : '5',
        'JUN' : '6',
        'JUL' : '7',
        'AUG' : '8',
        'SEP' : '9',
        'OCT' : '10',
        'NOV' : '11',
        'DEC' : '12'
    }

    parse_date = Date.split(" ")

    month = monthToNum[parse_date[0]]
    date = parse_date[1]
    year = parse_date[2]

    return year
def month_get(Date):
    monthToNum = {
        'JAN' : '1',
        'FEB' : '2',
        'MAR' : '3',
        'APR' : '4',
        'MAY' : '5',
        'JUN' : '6',
        'JUL' : '7',
        'AUG' : '8',
        'SEP' : '9',
        'OCT' : '10',
        'NOV' : '11',
        'DEC' : '12'
    }

    parse_date = Date.split(" ")

    month = monthToNum[parse_date[0]]
    date = parse_date[1]
    year = parse_date[2]

    return month

# store links that were not scraped in this list
error = []

# iterate through all of the links
for index, row in df.iterrows():
    if pd.isna(row['URL']):
        print("index {} has missing URL".format(index))
    elif row['Scraped']:
        print("index {} has already been scraped".format(index))
    else:
        try:
            print("scraping text from index {}".format(index))
            # go to link
            driver.get(row['URL'])
            # extract text from the body of the website
            body = driver.find_element_by_xpath("/html/body/table/tbody").text
            # split body of the text by line
            split = body.splitlines()
            # extract station
            station = split[0].strip()
            # extract date and broadcast
            date_broadcast = split[1]
            date_broadcast_split = date_broadcast.split("  ")
            date, month = return_Date_str(date_broadcast_split[0])
            broadcast = date_broadcast_split[1].strip()

            # extract the first timestamp
            first_paragraph = split[2].split(" ")
            time = first_paragraph[0][3:]
            time = time.replace(":", "_").strip()
            am_pm = first_paragraph[1][:2].strip()

            # save the text of the body to a text file in the directory below (e.g. news_broadcasts_2008/KARE/1/KARE 2008-7-28 04_00_02PM KARE 11 AT 4.txt)
            filename = station + " " + date + " " + time + am_pm + " " + broadcast + ".txt"

            # get the yeat and month
            yearA = year_get(date_broadcast_split[0])
            monthA = month_get(date_broadcast_split[0])

            # store the scraing files into the locations that we want
            filepath = os.path.join("../GFData/", station_name, filename)
            file = open(filepath, "w")
            file.write(body)
            file.close()
            df.iloc[index, -1] = True
        except:
            print("failed to scrape text from index {}".format(index))

df.to_csv(programs_url_links)
driver.quit()
