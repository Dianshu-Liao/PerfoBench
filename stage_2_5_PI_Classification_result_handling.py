import pandas as pd
import tqdm
import re
import math


'''
Input the PI_Classification, and return the PI Type and Root Causes

Input Example:
###Optimized_Performance_Issue_Type
    [Responsiveness]


###Root_Causes
    [Scrolling of WebView]


Output Example:
PI Types: [Responsiveness]
Root Causes: [Scrolling of WebView]
'''
def get_PI_Type_and_root_causes(PI_Classification):
    PI_Types = PI_Classification.split('\n\n###Root_Causes')[0].split('###Optimized_Performance_Issue_Type\n    ')[1].strip()
    Root_Causes = PI_Classification.split('\n\n###Root_Causes')[1].strip()
    return PI_Types, Root_Causes



def handle_PI_Types_and_Root_Causes(PI_Types, Root_Causes):

    if PI_Types == '[N/A]':
        handled_PI_Types = '[N/A]'
    else:
        PI_Types = PI_Types.replace('[', '').replace(']', '')
        all_types = PI_Types.split(',')
        handled_PI_Types = []
        for each_type in all_types:
            if each_type == 'N/A':
                pass
            else:
                handled_PI_Types.append(each_type.strip())


    if Root_Causes == '[N/A]':
        handled_Root_Causes = '[N/A]'
    else:
        Root_Causes = Root_Causes.replace('[', '').replace(']', '')
        all_causes = Root_Causes.split(',')
        handled_Root_Causes = []
        for each_cause in all_causes:
            handled_Root_Causes.append(each_cause.strip())
    return handled_PI_Types, handled_Root_Causes



def get_Commit_Data_After_Third_Filter(is_perf_in_unique_commits_path='data/is_perf_in_unique_commits.csv',
                                       saved_commit_data_after_second_filter_path='data/Saved_Commit_Data_After_Second_Filter.csv',
                                       saved_commit_data_after_third_filter_path='data/Saved_Commit_Data_After_Third_Filter.csv'):
    is_perf_in_unique_commits = pd.read_csv(is_perf_in_unique_commits_path)
    saved_commit_data_after_second_filter = pd.read_csv(saved_commit_data_after_second_filter_path)

    commit_link_to_num = saved_commit_data_after_second_filter['commit_link'].value_counts().to_dict()
    # 统计num的分布
    num_to_num = {}
    for _, value in commit_link_to_num.items():
        if value in num_to_num:
            num_to_num[value] += 1
        else:
            num_to_num[value] = 1
    num_to_num = dict(sorted(num_to_num.items(), key=lambda x: x[0]))

    # 统计num_to_num中key<=5的value之和，并且计算它在所有commit中的比例
    total_num = 0
    num_to_num_total_num = 0
    for key, value in num_to_num.items():
        if key <= 5:
            total_num += value
        num_to_num_total_num += value
    print(f'key<=5的value之和: {total_num}')
    print(f'key<=5的value之和在所有commit中的比例: {total_num / num_to_num_total_num}')

    # 只保留saved_commit_data_after_third_filter中commit_link重复的行<=5的行
    saved_commit_data_after_second_filter = saved_commit_data_after_second_filter[
        saved_commit_data_after_second_filter['commit_link'].map(commit_link_to_num) <= 5]


    # df = saved_commit_data_after_second_filter.drop_duplicates(subset=['commit_title', 'commit_description'])

    saved_commit_data_after_second_filter['pi_types'] = ''
    saved_commit_data_after_second_filter['root_causes'] = ''

    for index, row in tqdm.tqdm(is_perf_in_unique_commits.iterrows(), total=is_perf_in_unique_commits.shape[0]):
        commit_title = row['commit_title']
        commit_description = row['commit_description']
        PI_Classification = row['PI_Classification']
        PI_Types, Root_Causes = get_PI_Type_and_root_causes(PI_Classification)

        handled_PI_Types, handled_Root_Causes = handle_PI_Types_and_Root_Causes(PI_Types, Root_Causes)



        if commit_description != 'EMPTY':
            is_perf_commit = saved_commit_data_after_second_filter[
                (saved_commit_data_after_second_filter['commit_title'] == commit_title) & (
                            saved_commit_data_after_second_filter['commit_description'] == commit_description)]
        else:
            is_perf_commit = saved_commit_data_after_second_filter[
                (saved_commit_data_after_second_filter['commit_description'].isna()) & (
                            saved_commit_data_after_second_filter['commit_title'] == commit_title)]





        saved_commit_data_after_second_filter.loc[is_perf_commit.index, 'pi_types'] = str(handled_PI_Types)
        saved_commit_data_after_second_filter.loc[is_perf_commit.index, 'root_causes'] = str(handled_Root_Causes)

    unique_commits = saved_commit_data_after_second_filter['commit_link'].unique()
    dict_commit_to_pi_types = {'commit_link': [], 'PI_type': []}
    for commit_link in unique_commits:
        commit = saved_commit_data_after_second_filter[
            saved_commit_data_after_second_filter['commit_link'] == commit_link]
        # 取第0行的unique_pi_types
        pi_types = commit['pi_types'].values[0]
        if pi_types == '[N/A]':
            pi_types = ['N/A']
        else:
            pi_types = eval(pi_types)
        dict_commit_to_pi_types['commit_link'].append(commit_link)
        dict_commit_to_pi_types['PI_type'].append(pi_types)
    df_commit_to_pi_types = pd.DataFrame(dict_commit_to_pi_types)
    # 统计每个PI Type的数量
    PI_Types_to_num = {}
    for _, row in tqdm.tqdm(df_commit_to_pi_types.iterrows(), total=df_commit_to_pi_types.shape[0]):
        pi_types = row['PI_type']
        for pi_type in pi_types:
            if pi_type in PI_Types_to_num:
                PI_Types_to_num[pi_type] += 1
            else:
                PI_Types_to_num[pi_type] = 1
    # 按照value从大到小排序
    PI_Types_to_num = dict(sorted(PI_Types_to_num.items(), key=lambda x: x[1], reverse=True))

    #删除saved_commit_data_after_second_filter中pi_types==[N/A]的行
    saved_commit_data_after_third_filter = saved_commit_data_after_second_filter[~(saved_commit_data_after_second_filter['pi_types'] == '[N/A]')]
    saved_commit_data_after_third_filter.to_csv(saved_commit_data_after_third_filter_path, index=False)


def PI_classification_Statistic(saved_commit_data_after_third_filter_path='data/Saved_Commit_Data_After_Third_Filter.csv'):
    saved_commit_data_after_third_filter = pd.read_csv(saved_commit_data_after_third_filter_path)
    #去掉saved_commit_data_after_third_filter中commit_link重复的行
    saved_commit_data_after_third_filter = saved_commit_data_after_third_filter.drop_duplicates(subset=['commit_link'])
    PI_Types_to_num = {}
    for _, row in tqdm.tqdm(saved_commit_data_after_third_filter.iterrows(), total=saved_commit_data_after_third_filter.shape[0]):
        pi_types = eval(row['pi_types'])

        for pi_type in pi_types:
            if pi_type == 'N/A':
                continue
            if pi_type in PI_Types_to_num:
                PI_Types_to_num[pi_type] += 1
            else:
                PI_Types_to_num[pi_type] = 1

    #按照value从大到小排序
    PI_Types_to_num = dict(sorted(PI_Types_to_num.items(), key=lambda x: x[1], reverse=True))

    #print each PI Type and its number
    for key, value in PI_Types_to_num.items():
        print(f'{key}: {value}')

def final_handling_to_merge_PI_types(saved_commit_data_after_third_filter_path='data/Saved_Commit_Data_After_Third_Filter.csv',
                                     saved_commit_data_after_third_filter_with_PI_classification_format_path='data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv'):
    saved_commit_data_after_third_filter = pd.read_csv(saved_commit_data_after_third_filter_path)



    commit_link_to_num = saved_commit_data_after_third_filter['commit_link'].value_counts().to_dict()
    # 统计num的分布
    num_to_num = {}
    for _, value in commit_link_to_num.items():
        if value in num_to_num:
            num_to_num[value] += 1
        else:
            num_to_num[value] = 1
    num_to_num = dict(sorted(num_to_num.items(), key=lambda x: x[0]))

    #统计num_to_num中key<=5的value之和，并且计算它在所有commit中的比例
    total_num = 0
    num_to_num_total_num = 0
    for key, value in num_to_num.items():
        if key <= 5:
            total_num += value
        num_to_num_total_num += value
    print(f'key<=5的value之和: {total_num}')
    print(f'key<=5的value之和在所有commit中的比例: {total_num/num_to_num_total_num}')


    #只保留saved_commit_data_after_third_filter中commit_link重复的行<=5的行
    saved_commit_data_after_third_filter = saved_commit_data_after_third_filter[saved_commit_data_after_third_filter['commit_link'].map(commit_link_to_num) <= 5]
    # unique_commits = saved_commit_data_after_third_filter['commit_link'].unique()
    saved_commit_data_after_third_filter['unique_pi_types'] = ''
    for index, row in tqdm.tqdm(saved_commit_data_after_third_filter.iterrows(), total=saved_commit_data_after_third_filter.shape[0]):
        pi_types = eval(row['pi_types'])
        unique_pi_types = []
        for pi_type in pi_types:
            #if pi_type is 'Responsiveness' or 'Efficiency' or 'Concurrency' or 'Concurrency Issues', this pi_type is set to 'Responsiveness'
            if pi_type == 'Responsiveness' or pi_type == 'Efficiency' or pi_type == 'Concurrency' or pi_type == 'Concurrency Issues':
                unique_pi_types.append('Responsiveness')
            elif pi_type == 'Memory Consumption':
                unique_pi_types.append('Memory Consumption')
            elif pi_type == 'Storage Consumption' or pi_type == 'Data Usage' or pi_type == 'Disk Space Consumption':
                unique_pi_types.append('Storage Consumption')
            elif pi_type == 'Energy Consumption':
                unique_pi_types.append('Energy Consumption')
            elif pi_type == 'Build Time' or pi_type == 'Build Speed' or pi_type == 'Compilation Time' or pi_type == 'Compilation Speed'  or pi_type == 'Compile Time' or pi_type == 'Build Performance' or pi_type == 'Testing Time':
                unique_pi_types.append('Compilation Time')
            elif pi_type == 'CPU Consumption' or pi_type == 'CPU Usage' or pi_type == 'CPU Utilization' or pi_type == 'CPU Load' or pi_type == 'CPU Time':
                unique_pi_types.append('CPU Usage')
            elif pi_type == 'Network Performance' or pi_type == 'Network Consumption' or pi_type == 'Bandwidth Consumption' or pi_type == 'Network Traffic':
                unique_pi_types.append('Network Performance')
            elif pi_type == 'Graphics Rendering':
                unique_pi_types.append('Graphics Rendering')
            elif pi_type == 'Scalability':
                unique_pi_types.append('Scalability')
            elif pi_type == 'Image Processing' or pi_type == 'Security' or pi_type == 'CPU Ranking' or pi_type == 'Code Optimization' or pi_type == 'Data Transfer' or pi_type == 'CPU Cycles' or pi_type == 'IO Performance' or pi_type == 'Compatibility':
                pass
            else:
                raise ValueError(f'Unknown pi_type: {pi_type}')

        saved_commit_data_after_third_filter.loc[index, 'unique_pi_types'] = str(unique_pi_types)
    saved_commit_data_after_third_filter.to_csv(saved_commit_data_after_third_filter_with_PI_classification_format_path, index=False)




def calculate_sample_size(population_size, confidence_level=0.95, margin_of_error=0.05, proportion=0.5):
    # Z-score for the desired confidence level
    z_score = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576
    }[confidence_level]

    # Initial sample size calculation for an infinite population
    p = proportion
    e = margin_of_error
    z = z_score

    initial_sample_size = (z**2 * p * (1 - p)) / e**2

    # Adjust the sample size for a finite population
    adjusted_sample_size = initial_sample_size / (1 + (initial_sample_size - 1) / population_size)

    return math.ceil(adjusted_sample_size)

def sample_dataset_for_each_PI_Type():
    saved_commit_data_after_third_filter = pd.read_csv('data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv')
    unique_commits = saved_commit_data_after_third_filter['commit_link'].unique()

    dict_commit_to_pi_types = {'commit_link': [], 'PI_type': []}
    for commit_link in unique_commits:
        commit = saved_commit_data_after_third_filter[saved_commit_data_after_third_filter['commit_link'] == commit_link]
        #取第0行的unique_pi_types
        pi_types = eval(commit['unique_pi_types'].values[0])
        dict_commit_to_pi_types['commit_link'].append(commit_link)
        dict_commit_to_pi_types['PI_type'].append(pi_types)
    df_commit_to_pi_types = pd.DataFrame(dict_commit_to_pi_types)
    #统计每个PI Type的数量
    PI_Types_to_num = {}
    for _, row in tqdm.tqdm(df_commit_to_pi_types.iterrows(), total=df_commit_to_pi_types.shape[0]):
        pi_types = row['PI_type']
        for pi_type in pi_types:
            if pi_type in PI_Types_to_num:
                PI_Types_to_num[pi_type] += 1
            else:
                PI_Types_to_num[pi_type] = 1
    #按照value从大到小排序
    PI_Types_to_num = dict(sorted(PI_Types_to_num.items(), key=lambda x: x[1], reverse=True))

    sample_dataset = pd.DataFrame()

    #为每一类PI Type抽取样本
    for key, value in PI_Types_to_num.items():
        sample_size = calculate_sample_size(value)
        #从df_commit_to_pi_types中取出PI_type包含key的行并且随机抽取sample_size行
        sample_df = df_commit_to_pi_types[df_commit_to_pi_types['PI_type'].apply(lambda x: key in x)]
        # PI_type这一列变成str
        sample_df['PI_type'] = sample_df['PI_type'].apply(lambda x: str(x))
        sample_df = sample_df.sample(sample_size)

        #concatenate sample_df to sample_dataset
        sample_dataset = pd.concat([sample_dataset, sample_df], ignore_index=True)
        print('PI Type: {}, all num: {}, Sample Size: {}'.format(key, value, sample_size))

    sample_dataset = sample_dataset.drop_duplicates()
    commits = sample_dataset['commit_link'].to_list()
    #找到saved_commit_data_after_third_filter中commit_link在commits中的行
    sample_dataset_dict = {'commit_link': [], 'commit_title': [], 'commit_description': [], 'unique_pi_types': [], 'root_causes': []}

    # , 'PI_caused_class': [], 'PI_causes_method': [], 'PI_causes': [], 'optimization_method': []

    for commit in commits:
        #得到saved_commit_data_after_third_filter中commit_link==commit的行里面的第一个行
        commit_info = saved_commit_data_after_third_filter[saved_commit_data_after_third_filter['commit_link'] == commit].iloc[0]
        sample_dataset_dict['commit_link'].append(commit_info['commit_link'])
        sample_dataset_dict['commit_title'].append(commit_info['commit_title'])
        sample_dataset_dict['commit_description'].append(commit_info['commit_description'])
        sample_dataset_dict['unique_pi_types'].append(commit_info['unique_pi_types'])
        sample_dataset_dict['root_causes'].append(commit_info['root_causes'])
    sample_dataset_df = pd.DataFrame(sample_dataset_dict)
    sample_dataset_df['contain_perf'] = ''
    sample_dataset_df['PI_caused_class'] = ''
    sample_dataset_df['PI_causes_method'] = ''
    sample_dataset_df['PI_root_causes'] = ''
    sample_dataset_df['optimization_method'] = ''

    sample_dataset_df.to_csv('data/sample_dataset_for_labeling.csv', index=False)

if __name__ == '__main__':
    get_Commit_Data_After_Third_Filter()

    saved_commit_data_after_third_filter_path = 'data/Saved_Commit_Data_After_Third_Filter.csv'
    PI_classification_Statistic(saved_commit_data_after_third_filter_path)
    final_handling_to_merge_PI_types()

    # sample_dataset_for_each_PI_Type()
