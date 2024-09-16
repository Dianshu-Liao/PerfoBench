import pandas as pd
import tqdm
from file_util import FileUtil
import os
import pickle
def unzip_source_code(source_code_path):

    base_dir = os.path.dirname(source_code_path)
    extraction_folder = os.path.join(base_dir, 'extracted_project_code')
    # Ensure the extraction folder exists
    if not os.path.exists(extraction_folder):
        os.makedirs(extraction_folder)

    if source_code_path.endswith('.zip'):
        os.system('unzip -o ' + source_code_path + ' -d ' + extraction_folder)
    elif source_code_path.endswith('.tar.gz'):
        os.system('tar -zxvf ' + source_code_path + ' -C ' + extraction_folder)
    else:
        raise ValueError('Unknown file format')
    return extraction_folder

def find_source_code_paths(commit_dir):
    # 找到commit_dir文件夹下不是directory的所有文件
    all_files = os.listdir(commit_dir)
    source_code_paths = []
    for file in all_files:
        file_path = os.path.join(commit_dir, file)
        if not os.path.isdir(file_path):
            if not file_path.endswith('.apk'):

                source_code_paths.append(file_path)
    return source_code_paths


def check_commit_project_pair(commit_link, commit_project_pairs):
    #找到commit_project_pairs中commit_link这一列包含commit_link的行
    commit_project_pairs_row = commit_project_pairs[commit_project_pairs['commit_link'] == commit_link]

    if len(commit_project_pairs_row) == 0:
        raise ValueError('No commit link found in commit project pairs')
    elif len(commit_project_pairs_row) > 1:
        print('Multiple commit links found in commit project pairs')
        #!!!!!! this should be checked !!!!!!
        return True
        raise ValueError('Multiple commit links found in commit project pairs')
    else:
        check = commit_project_pairs_row['check'].values[0]
        if pd.isna(check):
            return False
        else:
            return True


def get_string_list_in_code_file(lines, file_path):
    string_list = []
    f = open(file_path, 'r')
    list_of_lines = f.readlines()
    f.close()

    for line in lines:
        string_list.append(list_of_lines[int(line)-1])
    return string_list


def check_purely_file_addition(file_path, before_change_dir, added_lines):
    after_change_dir = before_change_dir.replace('before_change', 'after_change')
    file_in_after_change_dir = os.path.join(after_change_dir, file_path)
    f = open(file_in_after_change_dir, 'r')
    list_of_lines = f.readlines()
    f.close()
    if len(list_of_lines) == len(added_lines):
        return True
    else:
        return False

def check_code_in_before_change_and_extracted_dir(before_change_dir, extraction_folder, commit_data, commit_link):
    corresponding_rows = commit_data[commit_data['commit_link'] == commit_link]
    if len(corresponding_rows) == 0:
        raise ValueError('No corresponding rows found')

    check_result = 'same'

    for index, row in corresponding_rows.iterrows():
        try:
            commit_diff_file = row['commit_diff_file']
            deleted_lines = eval(row['deleted_lines'])
            added_lines = eval(row['added_lines'])
            if commit_diff_file.endswith('.apk'):
                continue
            if commit_diff_file.endswith('.so'):
                continue
            # if this is purely a file addition, just judge there is no such file in before change dir
            if (deleted_lines == []) & (added_lines != []):
                if (check_purely_file_addition(commit_diff_file, before_change_dir, added_lines)):
                    file_in_before_change_dir = os.path.join(before_change_dir, commit_diff_file)
                    #check there is not such file in before change dir
                    if os.path.exists(file_in_before_change_dir):
                        check_result = 'different'
                        continue
                    else:
                        check_result = 'same'
                        continue


            file_in_before_change_dir = os.path.join(before_change_dir, commit_diff_file)
            content_in_before_change_dir = FileUtil.read_file(file_in_before_change_dir)

            string_list_before_change_file = get_string_list_in_code_file(deleted_lines, file_in_before_change_dir)

            # file_in_extracted_dir: 先得到extraction_folder的subdirectory，然后找到commit_diff_file
            sub_directories = FileUtil.subdirectories(extraction_folder)
            if len(sub_directories) == 0:
                raise ValueError('No subdirectories found in extraction folder')
            elif len(sub_directories) > 1:
                raise ValueError('Multiple subdirectories found in extraction folder')
            else:
                sub_directory = sub_directories[0]
                file_in_extracted_dir = os.path.join(sub_directory, commit_diff_file)
                if not os.path.exists(file_in_extracted_dir):
                    print('File not found: ' + file_in_extracted_dir)
                    check_result = 'different'
                    break
                content_in_extracted_dir = FileUtil.read_file(file_in_extracted_dir)
                for string in string_list_before_change_file:
                    if string.strip() not in content_in_extracted_dir:
                        check_result = 'different'
                        break
            if deleted_lines == []:
                if content_in_extracted_dir != content_in_before_change_dir:
                    check_result = 'different'
                    break
        except:
            continue
    if check_result == 'same':
        a = 1
    return check_result

def check_all_downloaded_apps(saved_projects_dir, commit_data_path, commit_project_pairs_path, unsuccessful_handled_commits_path):
    
    if os.path.exists(unsuccessful_handled_commits_path):
        with open(unsuccessful_handled_commits_path, 'rb') as file:
            unsuccessful_handled_commits = pickle.load(file)
    else:
        unsuccessful_handled_commits = []
    
    commit_data = pd.read_csv(commit_data_path)
    commit_project_pairs = pd.read_csv(commit_project_pairs_path)
    all_downloaded_apps = FileUtil.subdirectories(saved_projects_dir)

    for download_app in tqdm.tqdm(all_downloaded_apps):
        if download_app == 'data/Saved_Projects/SkyTubeTeam___SkyTubeLegacy':
            a = 1
        commit_hash_dirs = FileUtil.subdirectories(download_app)
        for commit_hash_dir in commit_hash_dirs:
            try:
                app_name = commit_hash_dir.split(saved_projects_dir + '/')[-1].split('/')[0]
                if '___' in app_name:
                    commit_link = 'https://github.com/{}/{}/commit/{}'.format(app_name.split('___')[0], app_name.split('___')[1], commit_hash_dir.split(app_name + '/')[-1])
                else:
                    commit_hash = commit_hash_dir.split(app_name + '/')[-1]
                    appname_and_commit_hash = app_name + '/commit/' + commit_hash
                    # 找到commit_data中commit_link这一列包含appname_and_commit_hash的行
                    commit_data_row = commit_data[commit_data['commit_link'].str.contains(appname_and_commit_hash)]
                    unique_commit_links = commit_data_row['commit_link'].unique()
                    if len(unique_commit_links) == 0:
                        raise ValueError('No commit link found in commit data')
                    elif len(unique_commit_links) > 1:
                        os.system('rm -rf ' + commit_hash_dir)
                        commit_link = []
                        for unique_commit_link in unique_commit_links:
                            commit_link.append(unique_commit_link)
                        raise ValueError('Multiple commit links found in commit data')
                    else:
                        commit_link = unique_commit_links[0]
    
                # judge whether the commit_link is checked in commit_project_pairs
                if check_commit_project_pair(commit_link, commit_project_pairs):
                    continue
    
                # perform the check
                before_change_dir = os.path.join(commit_hash_dir, 'before_change')
                source_code_paths = find_source_code_paths(commit_hash_dir)
                # 去掉source_code_paths中后缀为'.1'的文件
                source_code_paths = [source_code_path for source_code_path in source_code_paths if
                                     not source_code_path.endswith('.1')]
                if len(source_code_paths) > 1:
                    source_code_paths = sorted(source_code_paths, key=len)
                    source_code_paths = [source_code_paths[0]]
                if len(source_code_paths) == 0:
                    os.system('rm -rf ' + commit_hash_dir)
                    raise ValueError('No source code found')
                elif len(source_code_paths) == 1:
                    source_code_path = source_code_paths[0]
                    extraction_folder = unzip_source_code(source_code_path)
                    check_result = check_code_in_before_change_and_extracted_dir(before_change_dir, extraction_folder, commit_data,
                                                                  commit_link)
                    # commit_project_pairs的commit_link==commit_link的行的check列赋值为check_result
                    commit_project_pairs.loc[commit_project_pairs['commit_link'] == commit_link, 'check'] = check_result
                    if check_result == 'different':
                        #删除commit_hash_dir
                        os.system('rm -rf ' + commit_hash_dir)
                else:
                    raise ValueError('Multiple source code files found')

            except:
                if type(commit_link) == list:
                    unsuccessful_handled_commits += commit_link
                else:
                    unsuccessful_handled_commits.append(commit_link)
    with open(unsuccessful_handled_commits_path, 'wb') as file:
        pickle.dump(unsuccessful_handled_commits, file)

    commit_project_pairs.to_csv(commit_project_pairs_path, index=False)




if __name__ == '__main__':

    saved_projects_dir = 'data/Saved_Projects'
    commit_data_path = 'data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv'

    commit_project_pairs_path = 'data/commit_apk_pairs.csv'
    unsuccessful_handled_commits_path = 'data/unsuccessful_handled_commits.pkl'

    # commit_project_pairs['check'] = ''
    # commit_project_pairs.to_csv(commit_project_pairs_path, index=False)

    check_all_downloaded_apps(saved_projects_dir, commit_data_path, commit_project_pairs_path, unsuccessful_handled_commits_path)