import os

import pandas as pd
from utils import Util
import tqdm
def get_all_linkes(file_path):
    f = open(file_path)
    links = f.readlines()
    f.close()
    all_links = []
    for link in links:
        each_link = link.strip()
        all_links.append(each_link)
    return all_links




def merge_csvs():

    saved_commit_csvs = Util.get_all_subfiles('data/Saved_Commit_Data')

    # get all df from csvs and merge them. Logic: get all csvs in one time, then merget them, drop duplicates, save them
    all_saved_commits_dfs = []
    for csv in tqdm.tqdm(saved_commit_csvs):
        try:
            df = pd.read_csv(csv)
            all_saved_commits_dfs.append(df)
        except:
            os.remove(csv)
    all_saved_commits_df = pd.concat(all_saved_commits_dfs, ignore_index=True)
    all_saved_commits_df = all_saved_commits_df.drop_duplicates()
    all_saved_commits_df.to_csv('data/Saved_Commit_Data.csv', index=False)


if __name__ == '__main__':
    merge_csvs()