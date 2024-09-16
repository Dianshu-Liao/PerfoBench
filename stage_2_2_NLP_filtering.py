import pandas as pd
import tqdm
from file_util import FileUtil
import os
import tiktoken
import re
import requests


url = "http://localhost:11434/api/chat"

def llama3(messages):
    data = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=data)

    return (response.json()['message']['content'])

class Commit_Checker:
    LLM_Model = "gpt-4o"

    @staticmethod
    def find_words_between(text, word1, word2):
        pattern = word1 + r"(.*?)" + word2
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[0]

    @staticmethod
    def get_tobe_detected_files(repo_dir, suffix_list):
        matched_files = []

        # 将所有后缀统一为小写并移除前导的点（.）
        normalized_suffix_list = [suffix.lower().lstrip('.') for suffix in suffix_list]

        # 使用 os.walk 递归遍历目录树
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                # 获取文件后缀并转换为小写
                file_suffix = file.split('.')[-1].lower()
                if file_suffix in normalized_suffix_list:
                    # 将匹配的文件完整路径添加到列表中
                    matched_files.append(os.path.join(root, file))

        return matched_files

    @staticmethod
    def get_words_between(string, word1, word2):
        return string.split(word1)[-1].split(word2)[0]


    @staticmethod
    def get_tokens(prompt):
        prompt = str(prompt)
        embedding_encoding = "cl100k_base"
        encoding = tiktoken.get_encoding(embedding_encoding)
        tokens = encoding.encode(prompt)
        return tokens


    @staticmethod
    def get_prompt_examples(Prompt_Dir, Example_Num=5):
        example_prompt = []

        for i in range(1, Example_Num+1):
            Example_Dir = Prompt_Dir + '/Example{}'.format(i)
            Example_Input = FileUtil.read_prompt_file(Example_Dir + '/Input')
            Example_Output = FileUtil.read_prompt_file(Example_Dir + '/Output')
            example_user = {'role': 'user', 'content': Example_Input}
            example_assistant = {'role': 'assistant', 'content': Example_Output}
            example_prompt.append(example_user)
            example_prompt.append(example_assistant)
        return example_prompt


    @staticmethod
    def capture_Perf_and_Type(LLM_Result):
        Is_Perf = Commit_Checker.get_words_between(LLM_Result, '###Is_Perf_Optimization', '\n###Performance_Issue_Type')
        if '###Performance_Issue_Type' not in LLM_Result:
            return 'Not Match Format', 'Not Match Format'
        Performance_Issue_Type = LLM_Result.split('###Performance_Issue_Type')[-1]
        return Is_Perf, Performance_Issue_Type


    @staticmethod
    def prompt_construction(Commit_Title, Commit_Description, Prompt_Dir, Example_Num=3):
        system_prompt_path = Prompt_Dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_path)
        input_prompt_path = Prompt_Dir + '/Input'
        input_prompt = FileUtil.read_prompt_file(input_prompt_path)

        commit_title = FileUtil.add_tabs_to_string(Commit_Title, 1)
        commit_description = FileUtil.add_tabs_to_string(Commit_Description, 1)
        user_input_prompt = input_prompt.replace('#{}#', commit_title, 1)
        user_input_prompt = user_input_prompt.replace('#{}#', commit_description, 1)

        # example_prompt = Commit_Checker.get_prompt_examples(Prompt_Dir=Prompt_Dir, Example_Num=5)
        example_prompt = Commit_Checker.get_prompt_examples(Prompt_Dir=Prompt_Dir, Example_Num=Example_Num)

        system = [{'role': 'system', 'content': system_prompt}]
        user_input = [{'role': 'user', 'content': user_input_prompt}]

        input_prompt = system + example_prompt + user_input
        return input_prompt

    @staticmethod
    def Perf_and_Type_Extractor(Commit_Title, Commit_Description, Prompt_Dir):

        system_prompt_path = Prompt_Dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_path)
        input_prompt_path = Prompt_Dir + '/Input'
        input_prompt = FileUtil.read_prompt_file(input_prompt_path)


        commit_title = FileUtil.add_tabs_to_string(Commit_Title, 1)
        commit_description = FileUtil.add_tabs_to_string(Commit_Description, 1)
        user_input_prompt = input_prompt.replace('#{}#', commit_title, 1)
        user_input_prompt = user_input_prompt.replace('#{}#', commit_description, 1)

        example_prompt = Commit_Checker.get_prompt_examples(Prompt_Dir)


        system = [{'role': 'system', 'content': system_prompt}]
        user_input = [{'role': 'user', 'content': user_input_prompt}]


        # tokens_num = len(Commit_Checker.get_tokens(input_prompt))
        # print('tokens num: {}'.format(tokens_num))

        # input_prompt = system + user_input
        input_prompt = system + example_prompt + user_input

        # LLM_result = openai.ChatCompletion.create(model=LLM_Model, messages=input_prompt).choices[0]["message"]["content"]


        LLM_result = llama3(input_prompt)
        Is_Perf, Performance_Issue_Type = Commit_Checker.capture_Perf_and_Type(LLM_result)
        Is_Perf = Is_Perf.strip()
        Performance_Issue_Type = Performance_Issue_Type.strip()
        return Is_Perf, Performance_Issue_Type

def get_latest_batch_file(result_dir='data/is_perf_detect_results_ubuntu'):
    files = os.listdir(result_dir)
    files = [f for f in files if f.startswith('is_perf_detect_result_') and f.endswith('.csv')]
    if not files:
        return None
    max_num = max([int(re.findall(r'\d+', f)[0]) for f in files])
    return max_num


def remove_non_english_titles(df):
    # Drop rows where both commit_title and commit_description are NaN
    df = df.dropna(subset=['commit_title', 'commit_description'], how='all')

    # Function to check if the string contains only ASCII characters
    def is_english(text):
        return bool(re.match(r'^[\x00-\x7F]+$', text))

    # Filter out rows where commit_title contains non-English characters
    df_filtered = df[df['commit_title'].apply(lambda x: is_english(str(x)) if pd.notnull(x) else False)]

    return df_filtered



if __name__ == '__main__':



    # df = pd.read_csv('data/Saved_Commit_Data_After_First_Filter.csv')
    #
    #
    # unique_pairs = df.drop_duplicates(subset=['commit_title', 'commit_description'])
    # unique_pairs.to_csv('data/Unique_Commit_Data_After_First_Filter.csv', index=False)

    # unique_pairs = pd.read_csv('data/Unique_Commit_Data_After_First_Filter.csv')
    #
    # #split the unique_pairs into to parts. The first part is 2/3 of the total data, and the second part is 1/3 of the total data
    # first_part = unique_pairs.iloc[:int(len(unique_pairs)*2/3)]
    # second_part = unique_pairs.iloc[int(len(unique_pairs)*2/3):]
    # first_part.to_csv('data/First_Part_Unique_Commit_Data_After_First_Filter.csv', index=False)
    # second_part.to_csv('data/Second_Part_Unique_Commit_Data_After_First_Filter.csv', index=False)


    Prompt_Dir = 'Performance_Filter_Prompt'
    # unique_pairs = pd.read_csv('data/First_Part_Unique_Commit_Data_After_First_Filter.csv')
    unique_pairs = pd.read_csv('data/Second_Part_Unique_Commit_Data_After_First_Filter.csv')

    latest_batch = get_latest_batch_file()
    dict_is_perf_detection = {'commit_link': [], 'commit_title': [], 'commit_description': [], 'commit_hash': [],
                              'commit_diff_file': [], 'commit_diff': [], 'deleted_lines': [], 'added_lines': [], 'prompt': [],
                              'detect_result': []}

    batch_size = 500
    batch_number = latest_batch if latest_batch else 0
    start_index = batch_number


    for i, (_, row) in enumerate(tqdm.tqdm(unique_pairs.iterrows(), total=len(unique_pairs))):
        if i < start_index:
            continue

        commit_title = row['commit_title']
        commit_description = row['commit_description']
        commit_link = row['commit_link']
        commit_hash = row['commit_hash']
        commit_diff_file = row['commit_diff_file']
        commit_diff = row['commit_diff']
        deleted_lines = row['deleted_lines']
        added_lines = row['added_lines']
        if pd.isna(commit_description):
            commit_description = 'EMPTY'
        prompt = Commit_Checker.prompt_construction(commit_title, commit_description, Prompt_Dir)
        detect_result = llama3(prompt)

        dict_is_perf_detection['commit_link'].append(commit_link)
        dict_is_perf_detection['commit_title'].append(commit_title)
        dict_is_perf_detection['commit_description'].append(commit_description)
        dict_is_perf_detection['commit_hash'].append(commit_hash)
        dict_is_perf_detection['commit_diff_file'].append(commit_diff_file)
        dict_is_perf_detection['commit_diff'].append(commit_diff)
        dict_is_perf_detection['deleted_lines'].append(deleted_lines)
        dict_is_perf_detection['added_lines'].append(added_lines)
        dict_is_perf_detection['prompt'].append(prompt)
        dict_is_perf_detection['detect_result'].append(detect_result)

        if (i + 1) % batch_size == 0:
            batch_number += batch_size
            df_is_perf_detection = pd.DataFrame(dict_is_perf_detection)
            df_is_perf_detection.to_csv(f'data/is_perf_detect_results_ubuntu/is_perf_detect_result_{batch_number}.csv',
                                        index=False)
            dict_is_perf_detection = {key: [] for key in
                                      dict_is_perf_detection}  # Reset the dictionary for the next batch

    if dict_is_perf_detection['commit_link']:
        batch_number += batch_size
        df_is_perf_detection = pd.DataFrame(dict_is_perf_detection)
        df_is_perf_detection.to_csv(f'data/is_perf_detect_results_ubuntu/is_perf_detect_result_{batch_number}.csv',
                                    index=False)