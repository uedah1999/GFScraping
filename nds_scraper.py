# This file is used to iterate through each url,
# scrape the text within the url, and store it in the directory we want.
# Written by Nobuaki Masaki '20 in June 2019
# Revised by Xinyan Xiang '22 in July 2020
# Revised by Hiromichi Ueda '21 in February 2021
# 
# Last execution in macOS Big Sur in March 2021 
# with Python 3.8.3, Selenium 3.141.0, Pandas 1.2.0

import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# format the date for filename
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

    return year + "-" + month + "-" + date

def nds_scrape(programs_file, unscraped_programs_file, driver_option):
    df = pd.read_csv(programs_file)
    driver = webdriver.Chrome(options=driver_option)

    print("scrape total of {} indices".format(df.shape[0]))
    # iterate through all of the links
    for index, row in df.iterrows():
        if row['URL'] == '':
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
                date = return_Date_str(date_broadcast_split[0]) #2008-7-28
                broadcast = date_broadcast_split[1].strip()

                # extract the first timestamp
                first_paragraph = split[2].split(" ")
                time = first_paragraph[0][3:]
                time = time.replace(":", "_").strip()
                am_pm = first_paragraph[1][:2].strip()

                # save the text of the body to a .txt file in the specified directory
                # filename = e.g. 'KARE 2008-7-28 04_00_02PM KARE 11 AT 4.txt'
                filename = station + " " + date + " " + time + am_pm + " " + broadcast + ".txt"

                # specify directory
                file_dir = '../GFData/{}'.format(station)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                filepath = os.path.join(file_dir, filename)
                file = open(filepath, "w")
                file.write(body)
                file.close()
                df.loc[index, 'Scraped'] = True
            except:
                print("failed to scrape text from index {}".format(index))

        if (index + 1)%50==0: # update csv file after 50 iterations
            df_unscraped = df[~df['Scraped']] # programs that were not scraped
            df.to_csv(programs_file, index=False)
            df_unscraped.to_csv(unscraped_programs_file, index=False)        

    df_unscraped = df[~df['Scraped']] # programs that were not scraped
    df.to_csv(programs_file, index=False)
    df_unscraped.to_csv(unscraped_programs_file, index=False)
    driver.quit()
