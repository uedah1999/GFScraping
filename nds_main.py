# High-level code to run select_urls, nds_crawler, unique_program, and nds_scraper
# Written by Hiromichi Ueda '21 in February 2021
#
# Last execution in macOS Big Sur in March 2021 
# with Python 3.8.3, Selenium 3.141.0, Pandas 1.2.0

from unique_program import get_unique_program
from nds_crawler import nds_crawl
from select_urls import select_urls
from nds_scraper import nds_scrape

import pandas as pd
import os
import sys

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

username = 'REPLACE_THIS'
password = 'REPLACE_THIS'
nds_xls = '../GFData/Pt2.xls' # Excel file downloaded from 
programs_file = '../GFData/Pt2_programs.csv' # csv file to store programs
urls_file = '../GFData/Pt2_url_all.csv' # csv file to store all the urls from queries related to each program
failed_query_file = '../GFData/Pt2_failed_query.csv' # csv file to write which queries have encountered fatal error
unscraped_programs_file = '../GFData/Pt2_unscraped.csv' # csv file to store programs that need to be scraped.

if 'REPLACE_THIS' in [username, password]:
    sys.exit('Please provide valid NDS login information.')

get_unique_program(nds_xls, programs_file)
nds_crawl(username, password, programs_file, urls_file, failed_query_file, driver_option=op)
select_urls(urls_file, programs_file)
nds_scrape(programs_file, unscraped_programs_file, driver_option=op)