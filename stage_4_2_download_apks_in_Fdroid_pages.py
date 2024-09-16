import pandas as pd
from file_util import FileUtil
from selenium import webdriver
from selenium.webdriver.common.by import By
import tqdm
import os
import requests
from bs4 import BeautifulSoup


def get_Fdroid_csv(FDdata_dir):
    all_csv_files = FileUtil.get_all_files(FDdata_dir)
    all_csv_files = [file for file in all_csv_files if file.endswith('.csv')]
    merge_to_one = pd.DataFrame()
    for file in all_csv_files:
        df = pd.read_csv(file)
        merge_to_one = pd.concat([merge_to_one, df], ignore_index=True)
    merge_to_one = merge_to_one.drop_duplicates()
    return merge_to_one


def get_all_project_links():
    saved_commit_data_after_third_filter = pd.read_csv(
        'data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv')
    unique_commits = saved_commit_data_after_third_filter['commit_link'].unique()

    project_links = []
    for unique_commit in unique_commits:
        project_link = unique_commit.split('/commit/')[0]
        project_links.append(project_link)

    project_links = list(set(project_links))
    return project_links

def string_between(string, start, end):
    return string.split(start)[1].split(end)[0]

def find_all_apks_in_Fdroid_Pages(Fdroid_projects, saved_df_path, handled_github_links_path):

    if os.path.exists(handled_github_links_path):
        handled_github_links = FileUtil.read_pkl(handled_github_links_path)
    else:
        handled_github_links = []


    if os.path.exists(saved_df_path):
        saved_df = pd.read_csv(saved_df_path)
    else:
        saved_df = pd.DataFrame()
    saved_df = saved_df.drop_duplicates()
    batch_size = 10
    i = 1

    all_apks_info = {'gitLink': [], 'FDstoreLink': [], 'apk_release_time': [],
                              'apk_version': [], 'apk_code': [], 'apk_download_link': [], 'source_code_download_link': []}


    for index, row in tqdm.tqdm(Fdroid_projects.iterrows(), total=Fdroid_projects.shape[0]):
        FDroid_link = row['FDstoreLink']
        github_link = row['gitLink']
        if github_link in handled_github_links:
            continue

        response = requests.get(FDroid_link)
        if response.status_code == 404:
            print('404:', FDroid_link)
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        #找到 <ul class="package-versions-list">
        package_versions_list = soup.find('ul', class_='package-versions-list')
        #找到package_versions_list中的所有<li class="package-version">
        package_versions = package_versions_list.find_all('li', class_='package-version')
        for package_version in package_versions:
            header = package_version.find('div', class_="package-version-header")
            content = header.text
            try:
                apk_version = string_between(content, 'Version ', ' (')
                apk_code = content.split(apk_version + ' (')[1].split(')')[0]
                apk_release_time = content.split('Added on ')[-1].strip()
            except:
                a = 1

            source_code_p = package_version.find('p', class_='package-version-source')
            source_code_download_link = source_code_p.find('a')['href']
            apk_download_p = package_version.find('p', class_='package-version-download').find('b')
            apk_download_link = apk_download_p.find('a')['href']
            all_apks_info['gitLink'].append(github_link)
            all_apks_info['FDstoreLink'].append(FDroid_link)
            all_apks_info['apk_release_time'].append(apk_release_time)
            all_apks_info['apk_version'].append(apk_version)
            all_apks_info['apk_code'].append(apk_code)
            all_apks_info['apk_download_link'].append(apk_download_link)
            all_apks_info['source_code_download_link'].append(source_code_download_link)

        handled_github_links.append(github_link)



        if i % batch_size == 0:
            all_apks_info_df = pd.DataFrame(all_apks_info)
            saved_df = pd.concat([saved_df, all_apks_info_df], ignore_index=True)
            saved_df.to_csv(saved_df_path, index=False)
            handled_github_links = list(set(handled_github_links))
            FileUtil.write_list_to_pkl(handled_github_links, handled_github_links_path)

        i += 1
    saved_df.to_csv(saved_df_path, index=False)


if __name__ == '__main__':
    saved_df_path = 'data/all_apks_info_in_Fdroid_pages.csv'
    handled_github_links_path = 'data/handled_github_links_for_downloading_fdroid_apk_infos.pkl'
    Fdroid_csv = get_Fdroid_csv('data/FDdata')
    project_links = get_all_project_links()
    #找到Fdroid中的gitLink等于project_links中item的行
    Fdroid_projects = Fdroid_csv[Fdroid_csv['gitLink'].isin(project_links)]

    find_all_apks_in_Fdroid_Pages(Fdroid_projects, saved_df_path, handled_github_links_path)
