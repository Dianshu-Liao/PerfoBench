import pandas as pd
import tqdm
import re


'''
Aug 21, 2024 -> 2024-08-21
Jul 30, 2024 -> 2024-07-30
'''
def format_Fdroid_page_release_time(time_str):
    month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                  'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    year = time_str.split(',')[1].strip()
    month = month_dict[time_str.split(',')[0].split(' ')[0]]
    day = time_str.split(',')[0].split(' ')[1]
    return year + '-' + month + '-' + day


'''
2023-09-04T09:52:15Z -> 2023-09-04
'''
def format_release_time(time_str):
    return time_str.split('T')[0]


def get_useful_info(all_apks_info):
    all_useful_rows = []
    unique_git_links = all_apks_info['gitLink'].unique().tolist()

    for unique_git_link in tqdm.tqdm(unique_git_links):
        matched_rows = all_apks_info[all_apks_info['gitLink'] == unique_git_link]
        #找到matched_rows中download_file_name里面后缀是.apk的那一行, 不是包含.apk的那一行
        corresponding_apk_info = matched_rows[matched_rows['download_file_name'].str.endswith('.apk')]
        # corresponding_apk_info = matched_rows[matched_rows['download_file_name'].str.contains('.apk')]
        #得到apk_versions
        all_apk_versions = list(set(corresponding_apk_info['apk_version'].tolist()))
        for apk_version in all_apk_versions:
            necessary_rows = matched_rows[matched_rows['apk_version'] == apk_version]
            all_useful_rows.append(necessary_rows)
    #将all_useful_rows转换为dataframe，并且，index重置
    all_useful_apks_info = pd.concat(all_useful_rows)
    all_useful_apks_info = all_useful_apks_info.reset_index(drop=True)
    return all_useful_apks_info

def get_commit_data_pairs_in_Fdroid_Pages(all_apks_info_in_Fdroid_pages_path, all_saved_commit_data_path):

    dict_commit_data_pairs = {'gitLink': [], 'commit_link': [], 'commit_release_time': [], 'apk_release_time': [],
                              'apk_version': [], 'apk_download_link': [], 'source_code_download_link': []}

    all_apks_info_in_Fdroid_pages = pd.read_csv(all_apks_info_in_Fdroid_pages_path)
    all_apks_info_in_Fdroid_pages = all_apks_info_in_Fdroid_pages.drop_duplicates()

    saved_commit_data = pd.read_csv(all_saved_commit_data_path)

    #找到saved_commit_data中commit_release_time是nan的行
    saved_commit_data = saved_commit_data.dropna(subset=['commit_release_time'])


    all_git_links_in_Fdroid_page = all_apks_info_in_Fdroid_pages['gitLink'].unique().tolist()
    for git_link in tqdm.tqdm(all_git_links_in_Fdroid_page):
        matched_apk_rows = all_apks_info_in_Fdroid_pages[all_apks_info_in_Fdroid_pages['gitLink'] == git_link]
        matched_apk_rows['release_time'] = matched_apk_rows['apk_release_time'].apply(format_Fdroid_page_release_time)

        matched_saved_commit_data_rows = saved_commit_data[saved_commit_data['commit_link'].str.contains(git_link)]
        matched_saved_commit_data_rows['release_time'] = matched_saved_commit_data_rows['commit_release_time'].apply(format_release_time)
        matched_saved_commit_data_rows = matched_saved_commit_data_rows.drop_duplicates(subset='commit_link')

        for index, row in matched_saved_commit_data_rows.iterrows():
            commit_link = row['commit_link']
            commit_release_time = row['release_time']
            matched_apk_rows_before_commit = matched_apk_rows[matched_apk_rows['release_time'] < commit_release_time]
            if matched_apk_rows_before_commit.shape[0] == 0:
                continue
            matched_apk_rows_before_commit = matched_apk_rows_before_commit.sort_values(by='release_time', ascending=False)
            matched_apk_rows_before_commit = matched_apk_rows_before_commit.iloc[0]
            apk_version = matched_apk_rows_before_commit['apk_version']
            apk_release_time = matched_apk_rows_before_commit['release_time']
            apk_download_link = matched_apk_rows_before_commit['apk_download_link']
            source_code_download_link = matched_apk_rows_before_commit['source_code_download_link']
            dict_commit_data_pairs['gitLink'].append(git_link)
            dict_commit_data_pairs['commit_link'].append(commit_link)
            dict_commit_data_pairs['commit_release_time'].append(commit_release_time)
            dict_commit_data_pairs['apk_release_time'].append(apk_release_time)
            dict_commit_data_pairs['apk_version'].append(apk_version)
            dict_commit_data_pairs['apk_download_link'].append(apk_download_link)
            dict_commit_data_pairs['source_code_download_link'].append(source_code_download_link)

    df_commit_data_pairs = pd.DataFrame(dict_commit_data_pairs)
    return df_commit_data_pairs


def get_commit_data_pair_in_Fdroid(all_apks_info_in_Fdroid_path, all_saved_commit_data_path):
    dict_commit_data_pairs = {'gitLink': [], 'commit_link': [], 'commit_release_time': [], 'apk_release_time': [],
                              'apk_version': [], 'apk_download_link': [], 'source_code_download_link': [],
                              # 'changelog_link': []
                              }
    saved_commit_data = pd.read_csv(all_saved_commit_data_path)

    all_apks_info = pd.read_csv(all_apks_info_in_Fdroid_path)
    all_apks_info = all_apks_info.drop_duplicates()
    all_useful_apks_info = get_useful_info(all_apks_info)

    all_git_links = all_useful_apks_info['gitLink'].unique().tolist()
    for git_link in tqdm.tqdm(all_git_links):
        matched_apk_rows = all_useful_apks_info[all_useful_apks_info['gitLink'] == git_link]
        matched_apk_rows['release_time'] = matched_apk_rows['apk_release_time'].apply(format_release_time)

        matched_saved_commit_data_rows = saved_commit_data[saved_commit_data['commit_link'].str.contains(git_link)]
        matched_saved_commit_data_rows['release_time'] = matched_saved_commit_data_rows['commit_release_time'].apply(
            format_release_time)
        matched_saved_commit_data_rows = matched_saved_commit_data_rows.drop_duplicates(subset='commit_link')

        for index, row in matched_saved_commit_data_rows.iterrows():
            commit_link = row['commit_link']
            commit_release_time = row['release_time']
            matched_apk_info_before_commit = matched_apk_rows[matched_apk_rows['release_time'] < commit_release_time]
            if len(matched_apk_info_before_commit) == 0:
                continue
            # 找到matched_apk_info_before_commit中release_time最大的那一行
            matched_apk_info_before_commit = matched_apk_info_before_commit.sort_values(by='release_time',
                                                                                        ascending=False)
            matched_apk_info_before_commit = matched_apk_info_before_commit.iloc[0]
            apk_version = matched_apk_info_before_commit['apk_version']
            # changelog_link = matched_apk_info_before_commit['changelog_link']
            # unique_apk_versions = matched_apk_info_before_commit['apk_version'].unique().tolist()
            # for apk_version in unique_apk_versions:
            apk_info_rows = matched_apk_rows[matched_apk_rows['apk_version'] == apk_version]
            # 找到apk_info_rows中release_time最小的那一行对应的release_time
            apk_release_time = apk_info_rows['release_time'].min()
            # 找到download_file_name 这一列结尾是.apk的那一行
            apk_info = apk_info_rows[apk_info_rows['download_file_name'].str.contains('.apk')]
            # 去掉apk_info中download_file_name后缀不是.apk的那一行
            apk_info = apk_info[apk_info['download_file_name'].str.endswith('.apk')]

            # 找到download_file_name 这一列结尾是.zip的那一行
            zip_info = apk_info_rows[apk_info_rows['download_file_name'].str.contains('.zip')]
            if len(apk_info) == 1:
                apk_download_link = apk_info['download_link'].values[0]
                dict_commit_data_pairs['gitLink'].append(git_link)
                dict_commit_data_pairs['commit_link'].append(commit_link)
                dict_commit_data_pairs['commit_release_time'].append(commit_release_time)
                dict_commit_data_pairs['apk_release_time'].append(apk_release_time)
                dict_commit_data_pairs['apk_version'].append(apk_version)
                dict_commit_data_pairs['apk_download_link'].append(apk_download_link)
                # dict_commit_data_pairs['changelog_link'].append(changelog_link)
            elif len(apk_info) == 0:
                raise ValueError('no apk info!!!')
            else:

                # apk_info中download_file_name按照字符数量排序，取最短的那一行
                apk_info['download_file_name_len'] = apk_info['download_file_name'].apply(lambda x: len(x))
                apk_info = apk_info.sort_values(by='download_file_name_len', ascending=True)
                select_download_file_name = apk_info['download_file_name'].values[0]
                all_download_file_names = apk_info['download_file_name'].tolist()

                apk_download_link = apk_info['download_link'].values[0]

                if 'app-universal-release.apk' in all_download_file_names:
                    select_download_file_name = 'app-universal-release.apk'
                    apk_download_link = \
                    apk_info[apk_info['download_file_name'] == select_download_file_name]['download_link'].values[0]
                elif 'mobile.apk' in all_download_file_names:
                    select_download_file_name = 'mobile.apk'
                    apk_download_link = \
                    apk_info[apk_info['download_file_name'] == select_download_file_name]['download_link'].values[0]

                dict_commit_data_pairs['gitLink'].append(git_link)
                dict_commit_data_pairs['commit_link'].append(commit_link)
                dict_commit_data_pairs['commit_release_time'].append(commit_release_time)
                dict_commit_data_pairs['apk_release_time'].append(apk_release_time)
                dict_commit_data_pairs['apk_version'].append(apk_version)
                dict_commit_data_pairs['apk_download_link'].append(apk_download_link)
                # dict_commit_data_pairs['changelog_link'].append(changelog_link)

            if len(zip_info) == 1:
                source_code_download_link = zip_info['download_link'].values[0]
                dict_commit_data_pairs['source_code_download_link'].append(source_code_download_link)
            elif len(zip_info) == 0:
                raise ValueError('no zip info!!!')
            else:
                all_zip_file_names = zip_info['download_file_name'].tolist()

                if 'html.zip' in all_zip_file_names:
                    # 去掉html.zip 对应的行
                    zip_info = zip_info[zip_info['download_file_name'] != 'html.zip']

                zip_info['download_file_name_len'] = zip_info['download_file_name'].apply(lambda x: len(x))
                zip_info = zip_info.sort_values(by='download_file_name_len', ascending=True)
                select_download_file_name = zip_info['download_file_name'].values[0]

                source_code_download_link = \
                zip_info[zip_info['download_file_name'] == select_download_file_name]['download_link'].values[0]
                dict_commit_data_pairs['source_code_download_link'].append(source_code_download_link)

    df_commit_data_pairs = pd.DataFrame(dict_commit_data_pairs)
    return df_commit_data_pairs


def format_apk_versions(apk_versions_list):
    """
    Extracts version numbers from a list of strings and returns them in a formatted list.

    Args:
    apk_versions_list (list): A list of strings containing version information.

    Returns:
    list: A list of formatted version numbers.
    """
    # Extract version numbers using regex
    formatted_versions = [re.search(r'\d+(\.\d+)+', version).group() for version in apk_versions_list if
                          re.search(r'\d+(\.\d+)+', version)]

    return formatted_versions


if __name__ == '__main__':

    all_apks_info_in_Fdroid_pages_path = 'data/all_apks_info_in_Fdroid_pages.csv'
    all_apks_info_in_Fdroid_path = 'data/all_apks_info_in_github_release.csv'

    all_saved_commit_data_path = 'data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv'
    commit_data_pairs_in_Fdroid_pages = get_commit_data_pairs_in_Fdroid_Pages(all_apks_info_in_Fdroid_pages_path, all_saved_commit_data_path)


    commit_data_pairs_in_Fdroid = get_commit_data_pair_in_Fdroid(all_apks_info_in_Fdroid_path, all_saved_commit_data_path)

    unique_git_links_in_Fdroid_pages = commit_data_pairs_in_Fdroid_pages['gitLink'].unique().tolist()
    #增加commit_data_pairs_in_Fdroid里面没有cover到的在commit_data_pairs_in_Fdroid_pages中的行
    should_add_rows = []
    for git_link in unique_git_links_in_Fdroid_pages:
        corresponding_rows_in_Fdroid_pages = commit_data_pairs_in_Fdroid_pages[commit_data_pairs_in_Fdroid_pages['gitLink'] == git_link]
        corresponding_rows_in_Fdroid = commit_data_pairs_in_Fdroid[commit_data_pairs_in_Fdroid['gitLink'] == git_link]

        apk_versions_in_Fdroid = corresponding_rows_in_Fdroid['apk_version'].unique().tolist()
        formatted_apk_versions_in_Fdroid = format_apk_versions(apk_versions_in_Fdroid)

        apk_versions_in_Fdroid_pages = corresponding_rows_in_Fdroid_pages['apk_version'].unique().tolist()
        formatted_apk_versions_in_Fdroid_pages = format_apk_versions(apk_versions_in_Fdroid_pages)

        for apk_version in formatted_apk_versions_in_Fdroid_pages:
            if apk_version not in formatted_apk_versions_in_Fdroid:
                should_add_rows.append(corresponding_rows_in_Fdroid_pages[corresponding_rows_in_Fdroid_pages['apk_version'] == apk_version])
    #将should_add_rows转换为dataframe，并且，index重置, 然后和commit_data_pairs_in_Fdroid合并
    should_add_rows = pd.concat(should_add_rows)
    should_add_rows = should_add_rows.reset_index(drop=True)
    commit_data_pairs = pd.concat([commit_data_pairs_in_Fdroid, should_add_rows], ignore_index=True)

    commit_data_pairs.to_csv('data/commit_apk_pairs.csv', index=False)

