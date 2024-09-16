import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import tqdm
import pickle
from utils import Util
import random
from file_util import FileUtil
import re

def get_commit_release_time(commit_link):
    commit_response = requests.get(commit_link)
    #if 404, return None
    if commit_response.status_code == 404:
        return None
    soup = BeautifulSoup(commit_response.text, 'html.parser')
    target_div = soup.find('div', class_='flex-self-start flex-content-center')

    relative_time_tag = target_div.find('relative-time')
    datetime_value = relative_time_tag.get('datetime')
    return datetime_value

if __name__ == '__main__':

    while True:
        try:
            commit_data = pd.read_csv('data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv')
            # 去掉commit_data中commit_release_time不是NaN的行
            new_commit_data = commit_data[commit_data['commit_release_time'].isnull()]
            commit_links = new_commit_data['commit_link'].unique()
            if len(commit_links) == 0:
                break
            for commit_link in tqdm.tqdm(commit_links):
                commit_release_time = get_commit_release_time(commit_link)
                if commit_release_time is None:
                    continue
                # 为commit_data中的commit_link相同的所有行添加commit_release_time
                commit_data.loc[commit_data['commit_link'] == commit_link, 'commit_release_time'] = commit_release_time
        except:
            commit_data.to_csv('data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv', index=False)
            time.sleep(60)
