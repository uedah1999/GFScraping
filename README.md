# GFScraping
The scripts are written by Hiromichi Ueda '21, working for [the DataSquad](https://datasquad.at.sites.carleton.edu). They were last executed in February 2021.   
![alt text](./DataSquad_logo.png)   
This repository contains `.py` files to crawl and scrape news broadcast transcripts as `.txt` files, given an excel sheet from [News Data Service](https://newsdataservice.com) (NDS).   
In February 2021, a Colab notebook was added, which downloads videos of broadcast as mp4 files into Google Drive, given confirmation emails from NDS about clip request. 

## Requirement 
macOS Big Sur is the only environment in which the scripts have been executed
- [**Selenium**](https://selenium-python.readthedocs.io) (tested with Selenium 3.141.0)
- Python3 (tested with Python 3.8.3)
- Pandas (tested with Pandas 1.2.0)
- ChromeDriver
    - **DO NOT USE** `pip install chromedriver-binary` 
    - install Chrome and follow this [version selection guide](https://chromedriver.chromium.org/downloads/version-selection) to download the collect version
    - copy the `chromedriver.exe` file to `/usr/local/bin`

## How to collect transcripts for all programs in a folder from NDS
### Collect the necessary data
1. Log into [NDS portal](https://portal.newsdataservice.com/), using relevant account.
2. Under *Coverage* on the NDS website, select the folder of broadcasts you want to scrape. 
3. After clicking on the folders, click on *Export Data to Excel* button on the upper right corner of the *Coverage* page.  

Currently, NDS exports all selected folder as **a single excel sheet**.

### Check the XPaths of the scripts
The scripts depend on NDS website having a specific structure, since they use XPath of the website. In particular, you need to ensure that the XPaths in `return_Market_xpath(Market)`, `return_Source_xpath(Source)` functions in `nds_crawler.py` are up to date with the States, etc. selector on the NDS *Broadcast Content* [page](https://portal.newsdataservice.com/ProgramList).   
For details of how to check XPaths of elements, check [this blog](https://yizeng.me/2014/03/23/evaluate-and-validate-xpath-css-selectors-in-chrome-developer-tools/) or other information on the Internet.

### Choose the directories to store the transcripts
The project conducted in January 2021 was concerned with scraping a relatively small dataset of 442 transcripts from four stations. Thus, `nds_scraper.py` stores each transcript to the corresponding directory, determined solely based on station name.
```python
file_dir = '../GFData/{}'.format(station)
```
Based on the purpose of scraping, the directories should change, so make adjustments as needed. 

### Executing the scripts
Execute `nds_main.py` after changing the following variables and file paths:
- `username`, `password`: login information for NDS.
- `nds_xls`: the Excel sheet downloaded in the above *Collect the necessary data* section.
- `programs_file`: the csv file which stores each unique program in `nds_xls` with its Date, Time, Title, Source (station), Market (state & city / national), URL and Scraped status.
- `urls_file`: the csv file which stores the URLs obtained from queries based on programs in `programs_file`. Each query on NDS *Broadcast Content* [page](https://portal.newsdataservice.com/ProgramList) consists of States, Cities, Sources, and Program Date. Thus, `urls_file` includes the programs in `programs_file` and others that appear in one of the queries.
- `failed_query_file`: the csv file which stores the failed queries. More on failed queries in the *Scripts Logic* section.
- `unscraped_programs_file`: the csv file which stores the programs that were not scraped after the execution of the scripts. 

Each csv file has a header such as Date, Time, Title, Source (broadcast station), Market (state and city of the station), as needed by the corresponding functions.   
Execution will likely take quite a while. If you want to separate the process, you can comment out some of the last four lines. However, make sure to call the four functions in the original order:
```python
get_unique_program(nds_xls, programs_file)
nds_crawl(programs_file, urls_file, failed_query_file, driver_option=op)
select_urls(urls_file, programs_file)
nds_scrape(programs_file, driver_option=op)
```

If you need to check which programs need scraping, ***make sure to check `unscraped_programs_file`***. It is essential to the scripts that the date of each program is stored in ***yyyy-mm-dd format*** in all of the four csv files (e.g. *2020-06-06*). By default, Excel reformats this to *(m)m-(d)d-yy* format (e.g. *6/6/20*); thus, ***avoid manually modifying and saving the csv files***.

## How to collect transcripts for all programs from specific stations on specific dates
First, follow the **Check the XPaths of the script** and **Choose the directories to store the transcripts** sections above.  
Then, create a csv file with columns Date, Source and Market: for Market, look at `nds_crawler.py` to check the desired form of City/State combination; for Date, use yyyy-mm-dd format.
| Date | Source | Market |
| ---- | ------ | ------ |
| 2008-10-05 | WMSN | Madison, WI |
| 2008-10-05 | WKOW | Madison, WI |
| 2016-08-01 | KFXA | Cedar Rapids-Waterloo-Dubuque, IA |

Use this csv as `programs_file` and ran `nds_crawl()`. The new csv file `urls_file` has additional columns Time, Title, URL, Scraped. ***Do not save this csv file, since values in 'Scraped' column might become string value, not boolean.***
Now, use this new csv with 7 columns as `programs_file`, and ran `nds_scrape()`.

## How to use the Colab notebook for video clips
Upload all the emails from NDS as `.xml` files to a Google Driver folder, and adjust the filepaths accordingly. The notebook is similar to `nds_scraper.py`, thus a detailed script logic is omitted here.

## Updates of January 2021
The original scripts were written in June 2019, revised in July 2020, but had issues of 1) scraping unnecessary transcripts, and 2) missing necessary transcripts. Main updates of January 2021 include:
- Modified the crawling and scraping step to run Chrome WebDriver in background. 
- Transferred all scripts to Python in order to execute the whole process with a single file `nds_main.py`
- For each broadcast in the original excel file, the output csv file indicates
    1. whether the URL was collected
    1. whether the transcript was scraped  
- The crawler of the URLs accounts for the fact that some queries on NDS "fail" by taking too long.

## Scripts Logic
The main file `nds_main.py` executes `unique_program.py`, `nds_crawler.py`, `select_urls.py`, `nds_scraper.py` in this order. 

### `unique_program.py`
An excel file downloaded from NDS contains multiple entries of the same program, and each unique program is identified by its Date, Time, Title, Source (broadcast station) and Market (state & city / national).  
This script loads the excel file `nds_xls` downloaded from NDS, and creates a csv file `programs_file` that lists all the unique programs, sorted in the order of Market, Source, Date then Time. In `programs_file`, the Date and Time of each program match appearance in NDS.
- Date: *Jul 5 2020* in `nds_xls` &#8594; *2020-07-05* in `programs_file`
- Time: *8:00 AM CT* in `nds_xls` &#8594; *08:00AM CT* in `programs_file`

### `nds_crawler.py`
This script crawls / collects the URLs for the programs in `programs_file`. 
1. Identify the unique (Date, Source, Market) entries in `programs_file`
2. Conduct a query on NDS *Broadcast Content* [page](https://portal.newsdataservice.com/ProgramList), using each unique triplet:
    - For each program in the query results, copy its Date, Time, Title, Source, Market and its URL into `urls_file`
    - The script waits for 20 seconds for the query results to load. If the query results do not show up after 20 seconds, or if no URL is copied from the query, the query is classified as failure.
    - The script allows at most 10 failures for each query. If 10 failures are counted, the script ignores that query, and restarts from the next query.
3. Write to `failed_query_file` each query that failed 10 times in step 2.

Some queries succeed on some occasions and fail on others, and you can run the `nds_crawl(programs_file, urls_file, failed_query_file, driver_option)` function by updating `programs_file` to `failed_query_file`

### `select_urls.py`
For the programs of interest in `programs_file`, copy the URLs to their transcripts in `urls_file`. This script and `nds_crawler.py` are kept as separate files, since collecting the URLs from each query is already a complicated enough process. 
- Some programs in `programs_file` are missing in `urls_file` (from failed queries) and vice versa. 
- Some programs in `urls_file` come with missing Time and Title.

Thus, the script takes into account the above points:
1. Sort the programs in `programs_file` and `urls_file` in the same order of Market, Source, Date then Time. 
1. For each program in `urls_file` with missing Time and Title, fill in the two entries by parsing the obtained URL.
1. For each program in `programs_file`, check if its URL is in `urls_file` by comparing the unique identifier (Date, Time, Title, Source, Market). If its URL is found, copy it to *URL* column; otherwise, keep the entry empty.
1. Initialize *Scraped* column to all `False`.

### `nds_scraper.py`
For each program in `programs_file`, try scraping the transcript from the URL obtained in the above process
1. If the URL is missing, or if the transcript has already been scraped, then go to the next program
1. The transcript is successfully scraped, store the `.txt` file to appropriate path and update *Scraped* column to `True`
1. If scraping the transcript encounters some error, leave the *Scraped* column to `False`

For programs that were not scraped due to a missing URL or some error, write them as a csv file in `unscraped_programs_file`.

You can run the `nds_scrape(programs_file, driver_option)` function in this script multiple times until every program with a URL to the transcript is successfully scraped.