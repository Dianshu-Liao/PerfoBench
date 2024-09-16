import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import time
import tqdm
import pickle
from utils import Util
import random
from file_util import FileUtil
import re
import ipaddress


# 获取所有app的commits/main/的链接
def get_app_commits_main_url(path='./data/FDdata'):
    # 获取路径下所有CSV文件
    csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
    commits_links_list = []
    # 遍历所有CSV文件
    for file in csv_files:
        # 完整的文件路径
        full_path = os.path.join(path, file)
        # 读取CSV文件
        df = pd.read_csv(full_path)
        # 检查是否有 'gitlink' 列
        if 'gitLink' in df.columns:
            df['gitLink'].apply(lambda x: commits_links_list.append(x + '/commits'))
        else:
            print(f"文件：{file} 中没有 'gitLink' 属性")
    return list(set(commits_links_list))

def get_commits_number(github_link):
    response = requests.get(github_link)
    soup = BeautifulSoup(response.content, 'html.parser')
    span = soup.find('span', class_='Text-sc-17v1xeu-0 gPDEWA fgColor-default')
    if span != None:
        return ''.join(re.findall(r'\d+', span.text))
    else:
        print('span Not Found!')
        return None


def extract_project_content(url):
    return url.replace("https://github.com/", "")



def get_commits(saved_data_dir, commits_links_list, successful_saved_commits_page_links_path, successful_saved_projects_path, not_founded_links_path, threashold_of_commits):
    not_founded_links = Util.convert_file_lines_to_list(not_founded_links_path)
    successful_saved_commits_page_links = Util.convert_file_lines_to_list(successful_saved_commits_page_links_path)
    successful_saved_projects = Util.convert_file_lines_to_list(successful_saved_projects_path)
    # ---------------------------------------------for every application--commits----------------------------------------------
    # 获取每一个app的commit list
    for commits_link in tqdm.tqdm(commits_links_list):
        # if commits_link != 'https://github.com/mpcjanssen/simpletask-android/commits':
        #     continue

        if commits_link in successful_saved_projects:
            continue
        if commits_link in not_founded_links:
            continue
        if commits_link == 'https://github.com/scummvm/scummvm/commits':
            continue
        project_link = commits_link.strip('/commits')
        try:
            commit_nums = get_commits_number(project_link)
        except:
            print('wrong link:', project_link)
            write_successful_url(url=commits_link, file_path=not_founded_links_path)
            continue
        if commit_nums == None:
            write_successful_url(url=commits_link, file_path=not_founded_links_path)
            continue
        elif int(commit_nums) > threashold_of_commits:
            print(f"Too many commits: {commit_nums}")
            continue
        else:
            pass

        commit_file_id = 0
        has_next = True
        next_url = commits_link
        # page_num = 0
        # ---------------------------------------------for every page---------------------------------------------------
        while has_next:  # 如果有下一页，则翻页继续爬取
            print('url:{}, commit_file_id: {}'.format(next_url, commit_file_id))

            # 去除非github链接
            if not next_url.startswith("https://github.com/"):
                print('Not github link')
                write_successful_url(url=next_url, file_path=not_founded_links_path)
                break

            commit_data = []  # Each commit data contains all commit information within a commit page which contains multiple commits, for example, https://github.com//conchyliculture/wikipoff/commits
            fail_to_extract_all_data_in_a_commits_page = False
            current_url = next_url
            project_commit_link_name = extract_project_content(current_url).replace('/', '_').replace('?', '_')
            response = None
            for attempt in range(2):
                response = requests.get(next_url)
                try:
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    if str(e) == '404 Client Error: Not Found for url: ' + next_url:
                        print(f"404 Not Found: {e}")
                        write_successful_url(url=commits_link, file_path=not_founded_links_path)
                        has_next = False
                        break
                    print(f"tried {attempt + 1}/3 failed: {e}")
                    if attempt < 1:
                        print(f"retry after waiting for 2 seconds...")
                        time.sleep(2)
                    else:
                        has_next = False
                        print("Has already tried twice but doesn't work. stop trying...")
            if (has_next == False):
                break

            # commits list page
            soup = BeautifulSoup(response.content, 'html.parser')
            # print(soup)
            a_next = soup.find('a', {'data-testid': 'pagination-next-button'})
            if a_next != None:
                if 'disabled' in a_next.get('style', default='style'):
                    print('The last page')
                    has_next = False
                else:
                    next_url = f'https://github.com/' + a_next.get('href')
            else:
                print('Next button Not found!')
                has_next = False
            if current_url in successful_saved_commits_page_links:
                if has_next == False:
                    write_successful_url(url=commits_link, file_path=successful_saved_projects_path)
                continue

            divs = soup.find_all('div', {'data-testid': 'list-view-item-title-container'})
            # ---------------------------------------------for every file commit info in a commit--------------------------------------------
            for div in divs:
                # sleep_time = random.uniform(3, 4.5)
                # time.sleep(sleep_time)
                commit_title = div.text
                if commit_title == 'Initial commit':
                    continue
                # 获取div中的第一个a标签
                a_tag = div.find('a')
                commit_link = 'https://github.com' + a_tag['href'] # We can find the hash in this link

                if a_tag['href'] == None:
                    print('commit link Not found!')
                    continue

                # print(f"Commit Title: {commit_title}\nCommit Link: {commit_link}\n")
                try:
                    commit_response = requests.get(commit_link)
                except requests.exceptions.ConnectionError as e:
                    print(f'wrong link:{commit_link}')
                    continue
                except requests.exceptions.HTTPError as e:
                    print(f"failed trying: {e}")
                    fail_to_extract_all_data_in_a_commits_page = True
                    break

                # commit page
                commit_soup = BeautifulSoup(commit_response.content, 'html.parser')
                # 获取commit description
                commit_desc_div = commit_soup.find('div', class_='commit-desc')

                commit_desc = ''
                if (commit_desc_div != None):
                    commit_desc = commit_desc_div.find('pre').get_text(strip=True)
                # -----------------------------------------for every diff file------------------------------------------

                container_div = commit_soup.find('div', class_='js-diff-progressive-container')
                if container_div:
                    copilot_diff_entries = container_div.find_all('copilot-diff-entry')
                    # ----------------------------------------for every diff--------------------------------------------
                    for entry in copilot_diff_entries:
                        deleted_lines = []
                        added_lines = []
                        lines = entry.find_all('tr', class_='show-top-border')
                        commit_diff = ''
                        # ---------------------------------------for every lines----------------------------------------
                        for line in lines:
                            tds = line.find_all('td')
                            commit_diff += tds[-1].text
                            if 'blob-code-addition' in tds[-1].get('class', []):
                                added_lines.append(tds[1].get('data-line-number'))
                            elif 'blob-code-deletion' in tds[-1].get('class', []):
                                deleted_lines.append(tds[0].get('data-line-number'))
                        commit_data.append({
                            'commit_link': commit_link,
                            'commit_title': commit_title,
                            'commit_description': commit_desc,
                            'commit_hash': commit_link.split('/')[-1],
                            'commit_diff_file': entry['data-file-path'],
                            'commit_diff': commit_diff,
                            'deleted_lines': deleted_lines,
                            'added_lines': added_lines
                        })

            if fail_to_extract_all_data_in_a_commits_page == False:
                df = pd.DataFrame(commit_data)
                commit_file_name = saved_data_dir + '/' + project_commit_link_name + '.csv'
                df.to_csv(commit_file_name, index=False)
                write_successful_url(url=current_url, file_path=successful_saved_commits_page_links_path)
            commit_file_id += 1

            if has_next == False:
                write_successful_url(url=commits_link, file_path=successful_saved_projects_path)



def write_successful_url(url, file_path):
    f = open(file_path, 'a')
    f.writelines(url + '\n')
    f.close()


if __name__ == "__main__":
    successful_saved_commits_page_links_path = 'data/Successful_Saved_Commit_Page_Links.txt'
    successful_saved_projects_path = 'data/Successful_Saved_Projects.txt'
    not_founded_links_path = 'data/not_founded_links.txt'
    saved_data_dir = 'data/Saved_Commit_Data'
    # commits_links_list = get_app_commits_main_url()



    commits_link_list_path = 'data/commits_links_list.pkl'

    while True:
        try:
            commits_links_list = FileUtil.read_pkl(commits_link_list_path)

            all_not_founded_links = Util.get_all_linkes(not_founded_links_path)
            all_successful_saved_links = Util.get_all_linkes(successful_saved_projects_path)
            all_existing_links = list(set(all_not_founded_links + all_successful_saved_links))
            commits_links_list = list(set(commits_links_list) - set(all_existing_links))

            random.shuffle(commits_links_list)
            get_commits(saved_data_dir, commits_links_list, successful_saved_commits_page_links_path,
                                               successful_saved_projects_path, not_founded_links_path, threashold_of_commits=5000)
        except:
            print('exception! wait 30 seconds to rerun.')
            time.sleep(30)


