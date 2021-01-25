# Given an excel file imported from News Data Service (NDS),
# this file scrapes all the programs in the excel file.
# Written by Hiromichi Ueda in January 2021

from unique_program import get_unique_program
from nds_crawler import nds_crawl
from select_urls import select_urls
from nds_scraper import nds_scrape

import numpy as np
import pandas as pd
import csv
import os

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

nds_xls = '../GFData/Pt2.xls' # Excel file downloaded from 
programs_file = '../GFData/Pt2_programs.csv' # csv file to store programs
urls_file = '../GFData/Pt2_url_all.csv' # csv file to store all the urls from queries related to each program
failed_query_file = '../GFData/Pt2_failed_query.csv' # csv file to write which queries have encountered fatal error
unscraped_programs_file = '../GFData/Pt2_unscraped.csv' # csv file to store programs that need to be scraped.

get_unique_program(nds_xls, programs_file)
nds_crawl(programs_file, urls_file, failed_query_file, driver_option=op)
select_urls(urls_file, programs_file)
nds_scrape(programs_file, unscraped_programs_file, driver_option=op)