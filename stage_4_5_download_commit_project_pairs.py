import pandas as pd
import os
import subprocess
import pickle
import tqdm
import tqdm

def download_dataset(saved_projects_dir, commit_project_pair_path, record_info_csv_path, unsuccessful_saved_list_path, unsuccessful_handled_commits_path):
    # #在这个project的文件夹下，每个commit_hash就是一个子文件夹.
    # #commit hash更改之前的project算一个，commit hash 更改之后的project算一个。
    dict_record_info = {'gitLink': [], 'project_name': [], 'commit_link': [], 'commit_hash': [], 'before_change_dir': [], 'after_change_dir': [],
                        'commit_release_time': [], 'apk_release_time': [], 'apk_version': [], 'apk_download_link': [], 'source_code_download_link': []}
    # if os.path.exists(unsuccessful_saved_list_path):
    #     with open(unsuccessful_saved_list_path, 'rb') as file:
    #         unsuccessful_projects = pickle.load(file)
    # else:
    #     unsuccessful_projects = []


    # if os.path.exists(unsuccessful_handled_commits_path):
    #     with open(unsuccessful_handled_commits_path, 'rb') as file:
    #         unsuccessful_handled_commits = pickle.load(file)
    # else:
    #     unsuccessful_handled_commits = []

    commit_project_pair = pd.read_csv(commit_project_pair_path)
    commit_project_pair = commit_project_pair[commit_project_pair['check'].isna()]
    for index, row in tqdm.tqdm(commit_project_pair.iterrows(), total=commit_project_pair.shape[0]):
        try:
            gitLink = row['gitLink']
            commit_link = row['commit_link']

            # if commit_link in unsuccessful_handled_commits:
            #     continue
            apk_download_link = row['apk_download_link']
            source_code_download_link = row['source_code_download_link']
            commit_release_time = row['commit_release_time']
            apk_release_time = row['apk_release_time']
            apk_version = row['apk_version']


            project_name = gitLink.split('/')[-2] + '___' + gitLink.split('/')[-1]


            each_project_dir = os.path.join(saved_projects_dir, project_name)

            if os.path.exists(each_project_dir):
                pass
            else:
                os.makedirs(each_project_dir, exist_ok=True)

            project_link = gitLink + '.git'
            commit_hash = commit_link.split('/')[-1]

            each_hash_dir = os.path.join(each_project_dir, commit_hash)
            if os.path.exists(each_hash_dir):
                continue
            else:
                os.makedirs(each_hash_dir)

            # before commit change
            before_change_project_dir = os.path.join(each_hash_dir, 'before_change')
            if os.path.exists(before_change_project_dir):
                pass
            else:
                os.makedirs(before_change_project_dir)

            #如果before_change_project_dir中已经有文件，说明已经下载过了，直接跳过
            if os.listdir(before_change_project_dir):
                pass
            else:
                #download the project before the commit
                clone_command = f'git clone {project_link} {before_change_project_dir}'
                cd_to_dir = f'cd {before_change_project_dir}'
                checkout_command = f'git checkout {commit_hash}^'
                # 克隆仓库
                subprocess.run(clone_command, shell=True, check=True)
                # 检出特定的commit

                subprocess.run(f'{cd_to_dir} && {checkout_command}', shell=True, check=True)




            after_change_project_dir = os.path.join(each_hash_dir, 'after_change')

            if os.path.exists(after_change_project_dir):
                pass
            else:
                os.makedirs(after_change_project_dir)

            if os.listdir(after_change_project_dir):
                pass
            else:
                # after commit change
                clone_command = f'git clone {project_link} {after_change_project_dir}'
                cd_to_dir = f'cd {after_change_project_dir}'
                checkout_command = f'git checkout {commit_hash}'
                # 克隆仓库
                subprocess.run(clone_command, shell=True, check=True)
                # 检出特定的commit
                subprocess.run(f'{cd_to_dir} && {checkout_command}', shell=True, check=True)




            # download_apk_command = f'wget {apk_download_link} -P {each_hash_dir}'
            # download_source_code_command = f'wget {source_code_download_link} -P {each_hash_dir}'
            # #download apk and source code
            # subprocess.run(download_apk_command, shell=True, check=True)
            # subprocess.run(download_source_code_command, shell=True, check=True)


            dict_record_info['project_name'].append(project_name)
            dict_record_info['commit_link'].append(commit_link)
            dict_record_info['commit_hash'].append(commit_hash)
            dict_record_info['before_change_dir'].append(before_change_project_dir)
            dict_record_info['after_change_dir'].append(after_change_project_dir)
            dict_record_info['gitLink'].append(gitLink)
            dict_record_info['commit_release_time'].append(commit_release_time)
            dict_record_info['apk_release_time'].append(apk_release_time)
            dict_record_info['apk_version'].append(apk_version)
            dict_record_info['apk_download_link'].append(apk_download_link)
            dict_record_info['source_code_download_link'].append(source_code_download_link)
        except Exception as e:
            print(f'Error: {e}')
            # unsuccessful_handled_commits.append(commit_link)


    # #save unsuccessful_projects to pkl
    # with open(unsuccessful_saved_list_path, 'wb') as file:
    #     pickle.dump(unsuccessful_projects, file)

    #save unsuccessful_projects to pkl
    # with open(unsuccessful_handled_commits_path, 'wb') as file:
    #     pickle.dump(unsuccessful_handled_commits, file)

    df = pd.DataFrame(dict_record_info)
    df.to_csv(record_info_csv_path, index=False)

if __name__ == '__main__':
    saved_projects_dir = 'data/Saved_Projects'
    # commit_data_dir = 'data/Saved_Commit_Data'


    record_info_csv_path = 'data/dataset_info.csv'
    unsuccessful_saved_list_path = 'data/unsuccessful_saved_project_list.pkl'
    unsuccessful_handled_commits_path = 'data/unsuccessful_handled_commits.pkl'
    commit_project_pair_path = 'data/commit_apk_pairs.csv'


    download_dataset(saved_projects_dir, commit_project_pair_path, record_info_csv_path, unsuccessful_saved_list_path, unsuccessful_handled_commits_path)




