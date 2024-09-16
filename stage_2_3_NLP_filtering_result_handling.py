import pandas as pd
import tqdm
from file_util import FileUtil
from stage_2_2_NLP_filtering import Commit_Checker


def merge_is_perf_detect_results():


    is_perf_detect_result_dir = 'data/is_perf_detect_results'
    is_perf_detect_result_ubuntu_dir = 'data/is_perf_detect_results_ubuntu'

    df_is_perf_detect_result = FileUtil.merge_csv_files_in_directory(is_perf_detect_result_dir)
    df_is_perf_detect_result_ubuntu = FileUtil.merge_csv_files_in_directory(is_perf_detect_result_ubuntu_dir)

    #merge the two dataframes
    df = pd.concat([df_is_perf_detect_result, df_is_perf_detect_result_ubuntu], ignore_index=True)
    df = df.drop_duplicates()
    df.to_csv('data/Unique_Commits_Detect_Results.csv', index=False)

def propagate_is_perf_detect_results():


    all_necesarry_lines = []
    df = pd.read_csv('data/Unique_Commits_Detect_Results.csv')
    saved_commit_data = pd.read_csv('data/Saved_Commit_Data.csv')
    # saved_commit_data = pd.read_csv('data/Saved_Commit_Data_After_First_Filter.csv')

    for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
        detect_result = row['detect_result']
        ###Is_Perf_Optimization\n    No\n\n\n###Performance_Issue_Type\n    N/A

        Is_Perf_llama3, Performance_Issue_Type_llama3 = Commit_Checker.capture_Perf_and_Type(detect_result)
        Performance_Issue_Type = Performance_Issue_Type_llama3.strip()
        # if ('slow' in Performance_Issue_Type) | ('fast' in Performance_Issue_Type):
        #     all_necesarry_lines.append(row)
        if 'N/A' in Performance_Issue_Type:
            pass
        else:
            all_necesarry_lines.append(row)

    df_is_perf = pd.DataFrame(all_necesarry_lines)
    df_is_perf.to_csv('data/is_perf_in_unique_commits.csv', index=False)

    commit_link_list = df_is_perf['commit_link'].tolist()

    # is_perf_in_unique_commits = pd.read_csv('data/is_perf_in_unique_commits.csv')
    # commit_link_list = is_perf_in_unique_commits['commit_link'].tolist()
    saved_commit_data['is_perf'] = ''

    for index, row in tqdm.tqdm(df_is_perf.iterrows(), total=df_is_perf.shape[0]):
        commit_title = row['commit_title']
        commit_description = row['commit_description']
        if commit_description != 'EMPTY':
            # 找到saved_commit_data中commit_title和commit_description与is_perf_in_unique_commits中相同的行，并且这些行对应的is_perf的值为1
            is_perf_commit = saved_commit_data[(saved_commit_data['commit_title'] == commit_title) & (
                        saved_commit_data['commit_description'] == commit_description)]
        else:
            # 找到saved_commit_data中commit_description是nan并且commit_title与is_perf_in_unique_commits中相同的行，并且这些行对应的is_perf的值为1
            is_perf_commit = saved_commit_data[
                (saved_commit_data['commit_description'].isna()) & (saved_commit_data['commit_title'] == commit_title)]
        saved_commit_data.loc[is_perf_commit.index, 'is_perf'] = 1

    # saved_commit_data中is_perf为''的行，is_perf的值为0
    saved_commit_data['is_perf'] = saved_commit_data['is_perf'].apply(lambda x: 0 if x == '' else x)

    # unique_commits_detect_results = pd.read_csv('data/Unique_Commits_Detect_Results.csv')

    # 在saved_commit_data中，commit_link 属于commit_link_list的行，is_perf的值为1，否则为0
    for index, row in tqdm.tqdm(saved_commit_data.iterrows(), total=saved_commit_data.shape[0]):
        commit_link = row['commit_link']
        if commit_link in commit_link_list:
            saved_commit_data.at[index, 'is_perf'] = 1
        else:
            saved_commit_data.at[index, 'is_perf'] = 0
    # 找到saved_commit_data中is_perf是1的行。
    is_perf_commits = saved_commit_data[saved_commit_data['is_perf'] == 1]
    is_perf_commits.to_csv('data/Saved_Commit_Data_After_Second_Filter.csv', index=False)


if __name__ == '__main__':

    # df = pd.read_csv('data/just_temporatory_data_for_second_filter.csv')
    # df2 = pd.read_csv('data/Saved_Commit_Data_After_Second_Filter_temp.csv')
    # data_after_second_filter = pd.read_csv('data/Saved_Commit_Data_After_Second_Filter.csv')

    # merge_is_perf_detect_results()
    propagate_is_perf_detect_results()







