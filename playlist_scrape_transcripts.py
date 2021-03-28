

# HLPER FUNCTION: Get Time Now:
from datetime import datetime
def time_now():
    '''Get Current Time'''
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    return now


#imports here
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


from itertools import chain
from collections import Counter
from time import sleep


import pandas as pd
import regex as re


from youtube_transcript_api import YouTubeTranscriptApi
import os,sys
from random import random

folders_list = [name for name in os.listdir() if os.path.isdir(os.path.join(os.getcwd(), name))]
while True:
    print('Please enter the name of the folder output data to be saved in.')
    nlp_folder = input('Folder Name: ')
    nlp_folder = re.sub(r'\s+', '_', nlp_folder)
    nlp_folder = re.sub(r'_{2,}', '_', nlp_folder)
    try:
        if nlp_folder not in folders_list:
            os.mkdir(nlp_folder)
            print(f'{nlp_folder} folder was created in the working directory.')
            print(f'Check: {os.path.join(os.getcwd(), nlp_folder)}')
            break
    except:
        print('Something is wrong!')


print('Checking Selenium Webdriver path exists in the current directory:')
if 'chromedriver.exe' in os.listdir():
    driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    driver_path = driver_path.replace('\\', '/')
    if os.path.exists(driver_path):
        print('OK!')
else:
    while True:
        print('')
        print('Enter valid path for Selenium Chrome driver!')
        driver_path = input('Chrome Driver Path: ')
        if driver_path.startswith('"') and driver_path.endswith('"'):
            driver_path =  driver_path[1:-1]
        driver_path = driver_path.replace('\\', '/')
        if os.path.exists(driver_path) and driver_path.endswith('exe'):
            print('OK, you entered valid path.')
            break
        else:
            print('')
            print('Something went wrong! You didn\'t enter a valid path')



chrome_options = Options()

chrome_options.add_argument('--headless')
chrome_options.add_argument("--start-maximized")


print('Please Enter the YouTube playlist URL: ')
link = input('YouTube playlist URL: ')

############
print('Starting...')
start = time_now()
############

#1 opening chrome window
driver = webdriver.Chrome(driver_path, options=chrome_options)


driver.implicitly_wait(10)

#2 go to url
driver.get(link)


playlist_name_xpath = '//ytd-playlist-panel-renderer[@class="style-scope ytd-watch-flexy"]//h3//yt-formatted-string//a'
playlist_xpath = '//ytd-playlist-panel-renderer[@class="style-scope ytd-watch-flexy"]//div[@class="playlist-items style-scope ytd-playlist-panel-renderer"]//a[@id="wc-endpoint"]//a'


playlist_name = driver.find_element_by_xpath(playlist_name_xpath).text


playlist_name = re.sub(r'[\:\.\s\;\?\!\'\"\|\/]+', '_', playlist_name)
playlist_name = re.sub(r'_{2,}', '_', playlist_name)


print(f'The playlist name is: {playlist_name}')


vid_container = driver.find_elements_by_xpath(playlist_xpath)


links = [v.get_attribute('href') for v in vid_container]


links = [v.split('&list=')[0] for v in links]


links


numb_vids = len(links)


print(f'Number of videos transcripts to be scraped: {numb_vids}')


driver.quit()


youtube_vid_ids = [i.split('/watch?v=')[-1] for i in links]


def save_df_pickle(df, name_url_pickle_file):
    '''
    Given a pandas dataframe; save it with a given name.
    '''
    counter = 0
    if f'./{nlp_folder}/{name_url_pickle_file}.pkl' not in os.listdir():
        df.to_pickle(f'./{nlp_folder}/{name_url_pickle_file}.pkl', protocol=4)
        print(f'Pandas DataFrame was saved to ./{nlp_folder}/{name_url_pickle_file}.pkl in the current directory.')
    else:
        counter += 1
        pad = str(counter).zfill(2)
        df.to_pickle(f'./{nlp_folder}/{name_url_pickle_file}_copy_{pad}.pkl', protocol=4)
        print(f'Pandas DataFrame was saved to ./{nlp_folder}/{name_url_pickle_file}_copy{pad}.pkl in the current directory.')


def get_english_subs(x_list):
    '''Given a list of video_ids; get auto-generated subtitles using a YouTube api'''
    failed_list = []
    success_list = []
    print(f'Extracting cc will take at least {(len(x_list)*3)/60} minutes.')
    for vid_id in x_list:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)
            tra = transcript_list.find_transcript(['en'])
            subs = tra.fetch()
            success_list.append(subs)
            sleep(3)

        except:
            failed_list.append(vid_id)
    if len(failed_list) > 0:
        print('_'*50)
        print(f'{len(failed_list)} transcripts out of {numb_vids} couldn\'t be extracted')
        print('This could be because auto-generated cc wasn\'t enabled,\nOr English couldn\'t be recognized as the language of the video.')
        print('\n')
        print('The following videos couldn\'t be processed:')
        for i in failed_list:
            print(i)
            print('*'*50)
    else:
        print('All videos transcripts were extracted')
    
    print('\n')
    print(f'Only {len(success_list)} transcirpts were extracted.')
    return success_list


list_cc = get_english_subs(youtube_vid_ids)


len(list_cc)


new_cc = []
counter = 1
for i in list_cc:
    for j in i:
        new_cc.append((counter,j))
    counter +=1


df_subs = pd.DataFrame(data={'ID': [i[0] for i in new_cc],
                  'DUMMY': [i[1] for i in new_cc]})


df_subs['TEXT'] = df_subs['DUMMY'].apply(lambda x: x['text'])


df_subs['START'] = df_subs['DUMMY'].apply(lambda x: x['start'])


df_subs['DURATION'] = df_subs['DUMMY'].apply(lambda x: x['duration'])


df_subs = df_subs['ID	TEXT	START	DURATION'.split()]


df_subs['MINUTE'] = df_subs['START'].apply(lambda x: int(round(x/60, 0)+1))


grp_df_subs = df_subs.groupby(['ID', 'MINUTE']).agg({'TEXT': lambda x: ' '.join(x)})


grp_df_subs = grp_df_subs.reset_index()


# CREATE A FUNCTION THAT SAVES A PANDAS DATAFRAME! This is double work!
save_df_pickle(grp_df_subs, f'{playlist_name}_TRANSCRIPTS')
print('_'*50)
print(f'Save images & excel files to the following folder: {nlp_folder}')


############
print('Finished...')
end = time_now()
############
duration = end - start
duration_min = round(duration.seconds/60, 3)
if duration_min < 2:
    time_unit = 'minute'
else:
    time_unit = 'minutes'
print(f'Number of video transcripts: {len(list_cc)} out of {len(links)}.')
print(f'Total duration of scraping transcripts is {duration_min} {time_unit}.')


