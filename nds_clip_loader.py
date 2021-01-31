# Given eml files of emails from News Data Service,
# download clips from hyperlinks in each eml
# and write the downloading status in a csv file
# Written by Hiromichi Ueda in January 2021

import pandas as pd
import time
import requests
import email
import os
from email.header import decode_header
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# originally created by https://qiita.com/denzow/items/a42d344fa343cd80cf86 (in Japanese)
class MailParser(object):
    """
    parse an eml file whose path is given
    """

    def __init__(self, mail_file_path):
        self.mail_file_path = mail_file_path
        # obtain email.message.Message instance from eml file
        with open(mail_file_path, 'rb') as email_file:
            self.email_message = email.message_from_bytes(email_file.read())
        self.subject = None
        self.to_address = None
        self.cc_address = None
        self.from_address = None
        self.body = ""
        # dictionary for attachment
        # {name: file_name, data: data}
        self.attach_file_list = []
        self._parse()

    def get_attr_data(self):
        """
        obtain email data
        """
        result = """\
        FROM: {}
        TO: {}
        CC: {}
        SUBJECT: {}
        -----------------------
        BODY:
        {}
        -----------------------
        ATTACH_FILE_NAME:
        {}
        """.format(
            self.from_address,
            self.to_address,
            self.cc_address,
            self.subject,
            self.body,
            ",".join([ x["name"] for x in self.attach_file_list])
        )
        return result


    def _parse(self):
        """
        parse eml file
        called by __init__
        """
        self.subject = self._get_decoded_header("Subject")
        self.to_address = self._get_decoded_header("To")
        self.cc_address = self._get_decoded_header("Cc")
        self.from_address = self._get_decoded_header("From")

        # parse body
        for part in self.email_message.walk():
            # if ContentType is multipart, skip
            if part.get_content_maintype() == 'multipart':
                continue
            # obtain attachment file name
            attach_fname = part.get_filename()
            # if there is no attachment name, then parse the body
            if not attach_fname:
                charset = str(part.get_content_charset())
                if charset:
                    self.body += part.get_payload(decode=True).decode(charset, errors="replace")
                else:
                    self.body += part.get_payload(decode=True)
            else:
                # if there is an attachment name, obtain the file name and data
                self.attach_file_list.append({
                    "name": attach_fname,
                    "data": part.get_payload(decode=True)
                })

    def _get_decoded_header(self, key_name):
        """
        obtain decoded header
        """
        ret = ""

        # if no corresponding item, returl empty string
        raw_obj = self.email_message.get(key_name)
        if raw_obj is None:
            return ""
        # turn decoded result into unicode
        for fragment, encoding in decode_header(raw_obj):
            if not hasattr(fragment, "decode"):
                ret += fragment
                continue
            # unless encoding is specified, decode with utf-8
            if encoding:
                ret += fragment.decode(encoding)
            else:
                ret += fragment.decode("UTF-8")
        return ret

def get_program_name_url(nds_eml_path):
    result = MailParser(nds_eml_path)
    if result.subject.split(',')[0] != 'Media Archive Clip Processed':
        return False, '', ''
    else:
        program_name = ''
        program_url = ''
        for line in result.body.split('<br>'):
            if len(line) > 5:
                if line[:12]=='PROGRAM NAME': # Line containing clip name
                    program_name = line[14:]
                if line[:12]=='You can view': # Line containing the hyperlink
                    program_url = line.split('\"')[1]
        return True, program_name, program_url

def main(email_dir, csv_file_path, mp4_dir):
    # options to make webdriver run in the background
    op = Options()
    op.add_argument("--disable-gpu");
    op.add_argument("--disable-extensions");
    op.add_argument("--proxy-server='direct://'");
    op.add_argument("--proxy-bypass-list=*");
    op.add_argument("--start-maximized");
    op.add_argument("--headless");

    email_dir = '../GFEmail'
    programs_list = []

    print('scraping emails')
    for filename in os.listdir(email_dir):
        eml_file_path = email_dir + '/' + filename
        processed_eml, prog_name, prog_url = get_program_name_url(eml_file_path)
        if processed_eml:
            programs_list.append([prog_name, prog_url, False])
    df = pd.DataFrame(programs_list, columns=['name', 'url', 'downloaded'])
    df.to_csv(csv_file_path, index=False)
    print('emails have been scraped, start clip downloading')

    driver = webdriver.Chrome(options=op)
    for index, row in df.iterrows():
        prog_name = row['name']
        prog_url = row['url']
        driver.get(prog_url)
        time.sleep(20)
        if row['downloaded']:
            print('video has been downloaded from index {}'.format(index))
        else:
            try:
                mp4_link = driver.find_element_by_xpath('//*[@id="DownloadText"]/a').get_attribute('href')
                r = requests.get(mp4_link, stream = True)
                # download started  
                with open('{}/{}.mp4'.format(mp4_dir, prog_name), 'wb') as f:  
                    for chunk in r.iter_content(chunk_size = 1024*1024):
                        if chunk:
                            f.write(chunk)
                df.loc[index, 'downloaded'] = True
                print('downloaded clip from index {}'.format(index))
            except:
                print('failed to download clip from index {}'.format(index))
                driver.quit()
                driver = webdriver.Chrome(options=op)
    
        if index%20 == 0:
            df.to_csv(csv_file_path, index=False)
    driver.quit()
    df.to_csv(csv_file_path, index=False)

main(email_dir='../GFEmail', csv_file_path='../GFVideo/nds_clips.csv', mp4_dir='../GFVideo')