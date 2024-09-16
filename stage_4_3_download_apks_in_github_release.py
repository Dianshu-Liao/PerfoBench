import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from file_util import FileUtil
import tqdm
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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



def find_changelog_and_metadata(FDroid_link, github_link):
    response = requests.get(FDroid_link)
    if response.status_code == 404:
        print('404 not found: ', FDroid_link)
        return False, False
    soup = BeautifulSoup(response.content, 'html.parser')
    package_links = soup.find('ul', class_='package-links')
    li_items = package_links.find_all('li')
    exist_changelog = False
    exist_build_metadata = False
    for li_item in li_items:
        content = li_item.find('a').text.strip()
        if content == 'Changelog':
            exist_changelog = True
            changelog_link = li_item.find('a').get('href')
            releases_link = github_link + '/releases'
            if changelog_link != releases_link:
                return False, False
        if content == 'Build Metadata':
            exist_build_metadata = True
            build_metadata_link = li_item.find('a').get('href')
    if exist_changelog and exist_build_metadata:
        return changelog_link, build_metadata_link
    else:
        return False, False


def get_build_metadata(build_metadata_link):
    browser = webdriver.Chrome()
    browser.get(build_metadata_link)
    try:
        WebDriverWait(browser, 60).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'line'))
        )
    except:
        successful = False
        while not successful:
            try:
                WebDriverWait(browser, 60).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'line'))
                )
                successful = True
            except:
                time.sleep(5)
                print('waiting for build metadata to load...   ', build_metadata_link)
    try:
        code_lines = browser.find_elements(By.CLASS_NAME, 'line')
        code_snippets_list = [line.text for line in code_lines]
        code_content = '\n'.join(code_snippets_list)
    except:
        code_content = 'fail to get build metadata'
    return code_content


def get_changelog_info(changelog_link):
    changelog_link_template = changelog_link + '?page={}'
    changelog_info = {'changelog_link': [], 'apk_version': [], 'apk_release_time': [], 'download_link': [], 'download_file_name': []}

    page = 1
    while True:
        url = changelog_link_template.format(page)
        browser = webdriver.Chrome()
        browser.get(url)

        sections = browser.find_elements(By.TAG_NAME, 'section')
        if len(sections) == 0:
            break
        for section in sections:
            try:
                sr_only_element = section.find_element(By.CLASS_NAME, 'sr-only').text
            except:
                print('sr_only_element not found: ', url)
                continue
            try:
                span_element = section.find_element(By.XPATH,
                                                    ".//span[@data-view-component='true' and contains(@class, 'Label Label--warning Label--large v-align-text-bottom d-none d-md-inline-block')]").text
                if span_element == 'Pre-release':
                    continue
            except:
                pass

            box_footer = section.find_element(By.CLASS_NAME, "Box-footer")
            # div_mb3 = box_footer.find_element(By.CLASS_NAME, "mb-3")
            details_element = box_footer.find_element(By.TAG_NAME, 'details')
            summary_element = details_element.find_element(By.TAG_NAME, 'summary')
            summary_element.click()
            try:
                li_elements = WebDriverWait(details_element, 60).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'li'))
                )
            except:
                successful = False
                summary_element.click()
                while not successful:
                    try:
                        summary_element.click()
                        li_elements = WebDriverWait(details_element, 60).until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, 'li'))
                        )
                        if len(li_elements) > 0:
                            successful = True
                        else:
                            time.sleep(5)
                            print('waiting for li elements to load...   ', url)
                    except:
                        pass


            for li_element in li_elements:
                try:
                    a_element = li_element.find_element(By.TAG_NAME, 'a')
                except:
                    continue

                a_href = a_element.get_attribute('href')  # 获取 href 属性
                name = a_href.split('/')[-1]

                div_release_time = li_element.find_element(By.XPATH,
                                                        ".//div[contains(@class, 'd-flex flex-auto flex-justify-end')]")
                relative_time_element = div_release_time.find_element(By.TAG_NAME, 'relative-time')
                release_time_datetime = relative_time_element.get_attribute('datetime')

                apk_version = sr_only_element
                download_link = a_href
                download_file_name = name
                changelog_info['changelog_link'].append(changelog_link)
                changelog_info['apk_version'].append(apk_version)
                changelog_info['apk_release_time'].append(release_time_datetime)
                changelog_info['download_link'].append(download_link)
                changelog_info['download_file_name'].append(download_file_name)
        page += 1
    return changelog_info



def get_apk_download_info(FDroid_link, github_link):
    download_info = {'changelog_link': [], 'apk_version': [], 'apk_release_time': [], 'download_link': [],
                      'download_file_name': [], 'build_metadata': []}

    changelog_link, build_metadata_link = find_changelog_and_metadata(FDroid_link, github_link)
    if changelog_link and build_metadata_link:
        changelog_info = get_changelog_info(changelog_link)
        build_metadata = get_build_metadata(build_metadata_link)
        download_info['changelog_link'].extend(changelog_info['changelog_link'])
        download_info['apk_version'].extend(changelog_info['apk_version'])
        download_info['apk_release_time'].extend(changelog_info['apk_release_time'])
        download_info['download_link'].extend(changelog_info['download_link'])
        download_info['download_file_name'].extend(changelog_info['download_file_name'])
        download_info['build_metadata'].extend([build_metadata] * len(changelog_info['changelog_link']))

    return download_info




def find_all_apks_in_Fdroid(Fdroid_projects, saved_df_path, handled_github_links_path):

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
    all_apks_info = {'gitLink': [], 'FDstoreLink': [], 'changelog_link': [], 'apk_version': [], 'apk_release_time': [], 'download_link': [],
                      'download_file_name': [], 'build_metadata': []}


    for index, row in tqdm.tqdm(Fdroid_projects.iterrows(), total=Fdroid_projects.shape[0]):
        FDroid_link = row['FDstoreLink']
        github_link = row['gitLink']
        if github_link in handled_github_links:
            continue

        download_info = get_apk_download_info(FDroid_link, github_link)
        all_apks_info['gitLink'].extend([row['gitLink']] * len(download_info['changelog_link']))
        all_apks_info['FDstoreLink'].extend([FDroid_link] * len(download_info['changelog_link']))
        all_apks_info['changelog_link'].extend(download_info['changelog_link'])
        all_apks_info['apk_version'].extend(download_info['apk_version'])
        all_apks_info['apk_release_time'].extend(download_info['apk_release_time'])
        all_apks_info['download_link'].extend(download_info['download_link'])
        all_apks_info['download_file_name'].extend(download_info['download_file_name'])
        all_apks_info['build_metadata'].extend(download_info['build_metadata'])
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
    saved_df_path = 'data/all_apks_info_in_github_release.csv'
    handled_github_links_path = 'data/handled_github_links_for_downloading_android_apks.pkl'
    Fdroid_csv = get_Fdroid_csv('data/FDdata')
    project_links = get_all_project_links()
    #找到Fdroid中的gitLink等于project_links中item的行
    Fdroid_projects = Fdroid_csv[Fdroid_csv['gitLink'].isin(project_links)]
    find_all_apks_in_Fdroid(Fdroid_projects, saved_df_path, handled_github_links_path)
