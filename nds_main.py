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

station_name = 'KMSP'
nds_xls = '../GFData/{}_Pt1.xls'.format(station_name)
programs_file = '../GFData/{}_programs.csv'.format(station_name)
urls_file = '../GFData/{}_url_all.csv'.format(station_name)
failed_query_file = '../GFData/{}_failed_query.csv'.format(station_name)
programs_url_links = '../GFData/{}_url_programs.csv'.format(station_name)

get_unique_program(nds_xls, programs_file)
nds_crawl(programs_file, urls_file, failed_query_file, driver_option=op)
select_urls(urls_file, programs_file, programs_url_links)
nds_scrape(programs_url_links, driver_option=op)