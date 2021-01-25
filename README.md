# GFScraping
This repository contains files to crawl and scrape news broadcast transcripts from [News Data Service](https://newsdataservice.com) (NDS).

## Requirement 
macOS Big Sur is the only environment in which the scripts have been executed
- [**Selenium**](https://selenium-python.readthedocs.io) (tested with Selenium 3.141.0)
- Python3 (tested with Python 3.8.3)
- NumPy (tested with NumPy 1.19.4)
- Pandas (tested with Pandas 1.2.0)
- ChromeDriver
    - **DO NOT USE** `pip install chromedriver-binary` 
    - install Chrome and follow this [version selection guide](https://chromedriver.chromium.org/downloads/version-selection) to download the collect version
    - place the .exe file to /usr/local/bin

## How to use the scripts
### Collect the necessary data
1. Log into [NDS portal](https://portal.newsdataservice.com/), using relevant account.
2. Under *Coverage* on the NDS website, select the folder of broadcasts you want to scrape. 
3. After clicking on the folders, click on *Export Data to Excel* button on the upper right corner of the *Coverage* page.  

Currently, NDS exports all selected folder as **a single excel sheet**.

### Check the XPaths of the scripts
The scripts depend on NDS website having a specific structure, since it selects the information for query based on XPath. Namely, you need to ensure that the XPaths in `return_Market_xpath(Market)`, `return_Source_xpath(Source)` functions are up to date with the NDS *Broadcast Content* [page](https://portal.newsdataservice.com/ProgramList).   
For details of how to check XPaths of elements, check [this blog](https://yizeng.me/2014/03/23/evaluate-and-validate-xpath-css-selectors-in-chrome-developer-tools/) or other information on the Internet.

### Choose the directories to store the transcripts
The project conducted in January 2021 was concerned with scraping a relatively small dataset of 442 transcripts from four stations. Thus, `nds_scraper.py` stores each transcript to the corresponding directory, determined solely based on station name (line **FILL THIS IN**)
```python
filepath = os.path.join("../GFData/{}/".format(station), filename)
```
Based on the usage of the data, the directories will change, so make sure to change the file paths appropriately. 

## Update on January 2021
The original scripts were written in June 2019, revised in July 2020, but had issues of 1) scraping unnecessary transcripts, and 2) missing necessary transcripts. Main updates on January 2021 include:
- Transferred all scripts to Python in order to execute the whole process with a single file `nds_main.py`
- For each broadcast in the original excel file, the output csv file indicates
    1. whether the URL was collected
    2. whether the transcript was scraped  
- The crawler of the URLs account for the fact that some queries on NDS "fail" by taking too long.
