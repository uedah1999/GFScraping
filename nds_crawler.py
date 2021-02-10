# This code is used to downlowad all the stories' url links on to an excel spreadsheet
# Written by Nobuaki Masaki in June 2019
# Revised by Xinyan Xiang in July 2020
# Revised by Hiromichi Ueda in January 2021

import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# This function takes in the name of the market as input, and returns the x_path of the state and city as output.
# remember to go to NDS to check whether the x-path is right or not, since NDS may change the order of the Market name.
# To be more specific, you should check, for example,the numer (5, in this case) in "//*[@id="states_listbox"]/li[5].
def return_Market_xpath(Market):
    if Market == 'Minneapolis-St. Paul, MN':
        return ['//*[@id="states_listbox"]/li[5]', '//*[@id="cities_listbox"]/li[3]']

    if Market == 'Madison, WI':
        return ['//*[@id="states_listbox"]/li[7]', '//*[@id="cities_listbox"]/li[4]']

    if Market == 'Cedar Rapids-Waterloo-Dubuque, IA':
        return ['//*[@id="states_listbox"]/li[4]', '//*[@id="cities_listbox"]/li[1]']

# This function takes in the name of the station as input, and returns the x_path of the station as output.
# remember to go to NDS to check whether the x-path is right or not, since NDS may change the order of the source name.
def return_Source_xpath(Source):

    if Source == 'KARE':
        return '//*[@id="sources_listbox"]/li[2]'

    if Source == 'KMSP':
        return '//*[@id="sources_listbox"]/li[9]'

    if Source == 'KSTP':
        return '//*[@id="sources_listbox"]/li[16]'

    if Source == 'WCCO':
        return '//*[@id="sources_listbox"]/li[25]'

    if Source == 'KFXA':
        return '//*[@id="sources_listbox"]/li[3]'

    if Source == 'WMSN':
        return '//*[@id="sources_listbox"]/li[11]'

    if Source == 'WKOW':
        return '//*[@id="sources_listbox"]/li[10]'

    if Source == 'KGAN':
        return '//*[@id="sources_listbox"]/li[5]'

def nds_crawl(username, password, programs_file, urls_file, failed_query_file, driver_option):
    Programs_List = pd.read_csv(programs_file)
    # The three columns identify exactly what is needed to make a query in NDS
    Query_List = Programs_List.loc[:, ['Date', 'Source', 'Market']].drop_duplicates().reset_index(drop=True)

    links = [] # the list to store all the URLs
    failed_query = []
    query_idx = 0
    num_query = Query_List.shape[0]
    print("make {} total queries".format(num_query))

    while query_idx < num_query: # query is not completed
        Driver_Success = True # Driver has not encounterd a fatal failure

        # (re)start the webdriver in background
        driver = webdriver.Chrome(options=driver_option)
        # login
        driver.get('https://portal.newsdataservice.com/ProgramList')
        time.sleep(10)
        driver.find_element_by_xpath('//*[@id="Loginform"]/div/div[2]/div/p[3]/input').click()
        driver.find_element_by_xpath('//*[@id="Loginform"]/div/div[2]/div/p[3]/input').send_keys(username)
        driver.find_element_by_xpath('//*[@id="Loginform"]/div/div[2]/div/p[5]/input').click()
        driver.find_element_by_xpath('//*[@id="Loginform"]/div/div[2]/div/p[5]/input').send_keys(password)
        driver.find_element_by_xpath('//*[@id="submitBtn"]').click()
        time.sleep(10)

        # continue with the same driver while a query remains to be conducted
        # and the driver has not encounterd any fatal failure
        while Driver_Success and (query_idx < num_query): 
            row = Query_List.loc[query_idx,]
            # a list to store a program by its identification and its url
            programs = []
            print("Making " + str(query_idx) + "th query.")

            num_failed_attempt = 0
            Query_Success = False # status of most recent attempt of this particular query
            # until we succeed or make 10 failed attepts
            while (not Query_Success) and (num_failed_attempt < 10):
                # restart the attempt
                try:
                    # navigating to search
                    driver.find_element_by_xpath('//*[@id="navigation"]/li[6]/a').click()
                    time.sleep(3)

                    # defining fields to select
                    Market = row['Market']
                    Source = row['Source']
                    Date_str = row['Date']
                    Market_x_path = return_Market_xpath(Market)
                    State_x_path = Market_x_path[0]
                    City_x_path = Market_x_path[1]
                    Source_x_path = return_Source_xpath(Source)

                    # clicking on states box
                    driver.find_element_by_xpath('//*[@id="powerStates"]/div[5]/div/input').click()
                    time.sleep(1)
                    # selecting state
                    driver.find_element_by_xpath(State_x_path).click()
                    time.sleep(1)

                    # clicking on cities box
                    driver.find_element_by_xpath('//*[@id="powerCities"]/div[4]/div/input').click()
                    time.sleep(1)
                    # selecting city
                    driver.find_element_by_xpath(City_x_path).click()
                    time.sleep(1)

                    # clicking on source box
                    driver.find_element_by_xpath('//*[@id="srcWrapper"]/div/div').click()
                    time.sleep(1)
                    # selecting source
                    driver.find_element_by_xpath(Source_x_path).click()
                    time.sleep(1)

                    # clicking on date box
                    driver.find_element_by_xpath('//*[@id="datePrograms"]').click()
                    time.sleep(1)
                    # clearing default date from date box
                    driver.find_element_by_xpath('//*[@id="datePrograms"]').clear()
                    time.sleep(1)
                    # sending date
                    driver.find_element_by_xpath('//*[@id="datePrograms"]').send_keys(Date_str)
                    time.sleep(1)

                    # clicking submit
                    driver.find_element_by_xpath('//*[@id="btnListPrograms"]').click()
                    time.sleep(20)
                    
                    # collect all urls from the query
                    b = True
                    i = 0
                    while b:
                        i = i + 1
                        try:    
                            # extract link
                            xpath = '//*[@id="results"]/table/tbody/tr[' + str(i) + ']/td[5]/a'
                            onclick = driver.find_element_by_xpath(xpath).get_attribute('onclick')
                            url = onclick.split("'")[1]

                            # extract time and title of the program with the url
                            Time_str = driver.find_element_by_xpath('//*[@id="results"]/table/tbody/tr[' + str(i) + ']/td[3]').text
                            Title_str = driver.find_element_by_xpath('//*[@id="results"]/table/tbody/tr[' + str(i) + ']/td[4]').text

                            # attach the program identification and URL to the nested list
                            programs.append([Date_str, Time_str, Title_str, Source, Market, url])
                        except:
                            # if the next link does not exist, set b to false and exist query
                            b = False

                    print("num links collected: " + str(len(programs)))
                    time.sleep(3)
                    
                    Query_Success = True # the query attempt ran without error
                    if len(programs) > 0:
                        links = links + programs # add the programs from this success query
                    else:
                        failed_query.append([Date_str, Source, Market]) # no program is found

                except: # the query attempt has failed
                    num_failed_attempt += 1

            if not Query_Success: # all 10 attempts failed
                Driver_Success = False # encountered a fatal failure
                failed_query.append([Date_str, Source, Market])
                print("query has failed. quit and restart webdriver")
                driver.quit()
            
            query_idx += 1 # move on to the next query
    driver.quit()
    print("query complete")

    # write obtained URLs to a csv file
    df_urls = pd.DataFrame(links, columns=['Date', 'Time', 'Title', 'Source', 'Market', 'URL'])
    df_urls.to_csv(urls_file, index=False)

    # writing queries that encountered a fatal failure
    df_failed = pd.DataFrame(failed_query, columns=['Date', 'Souce', 'Market'])
    df_failed.to_csv(failed_query_file, index=False)