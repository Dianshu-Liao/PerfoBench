import pandas as pd
import os
from file_util import FileUtil
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


def get_all_commits(owner, repo):
    page = 1
    all_commits = []
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}"
        response = requests.get(url)
        commits = response.json()

        if len(commits) == 0:
            break

        all_commits.extend(commits)
        page += 1

    return all_commits


def get_code_diff(commit_link):
    code_diff_info = []
    commit_hash = commit_link.split('/')[-1]
    github_link = commit_link.split('/commit/')[0]
    project_name = github_link.split('/')[-1]
    user_name = github_link.split('/')[-2]
    output_file = 'commit_diff_output.json'

    github_commit_get_api_url = 'https://api.github.com/repos/{}/{}/commits/{}'.format(
        user_name, project_name, commit_hash)
    response = requests.get(github_commit_get_api_url)
    commit_info = response.json()

    commit_message = commit_info['commit']['message']

    commit_files = commit_info['files']

    for file in commit_files:

        file_name = file['filename']
        patch = file['patch']
        code_diff_info.append({'file_name': file_name, 'patch': patch})
    return commit_message, code_diff_info


def get_code_diff_formatted(code_diff_info):
    file_num = 1
    string_of_code_diffs = ''
    for code_diff in code_diff_info:
        file_name = code_diff['file_name']
        patch = code_diff['patch']
        patch = FileUtil.add_tabs_to_string(patch, 2)
        string_of_code_diffs += f'file {file_num}{{\n\tfile name: {file_name}\n\tpatch:\n{patch}\n}}\n'

        # string_of_code_diffs += 'file {}{\n\tfile name: {}\n\tpatch:\n{}\n\}\n'.format(file_num, file_name, patch)
        file_num += 1
    return string_of_code_diffs
def construct_code_diff_analysis_prompt(code_diff_analysis_prompt_dir, commit_message, code_diff_info):
    input_prompt_path = code_diff_analysis_prompt_dir + '/Input'
    input_prompt = FileUtil.read_prompt_file(input_prompt_path)

    commit_message = FileUtil.add_tabs_to_string(commit_message, 1)
    user_input_prompt = input_prompt.replace('#{}#', commit_message, 1)
    code_diff_format_info = get_code_diff_formatted(code_diff_info)
    code_diff_format_info = FileUtil.add_tabs_to_string(code_diff_format_info, 1)
    user_input_prompt = user_input_prompt.replace('#{}#', code_diff_format_info, 1)

    user_input = [{'role': 'user', 'content': user_input_prompt}]

    return user_input

if __name__ == '__main__':

    # json_result = FileUtil.load_json('all_commits_info_in_project.json')
    # a = 1
    # optimized_commits_path = 'data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv'
    code_diff_analysis_prompt_dir = 'Code_Diff_Analysis_Prompt'
    perfobench_path = 'data/perfobench.csv'

    optimized_commits = pd.read_csv(perfobench_path)
    unique_commit_links = optimized_commits['commit_link'].unique().tolist()
    github_links = []
    for commit_link in unique_commit_links:
        commit_message, code_diff_info = get_code_diff(commit_link)
        prompt = construct_code_diff_analysis_prompt(code_diff_analysis_prompt_dir, commit_message, code_diff_info)

        detect_result = llama3(prompt)
        print(detect_result)