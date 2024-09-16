import pandas as pd
import os
from file_util import FileUtil
import requests

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


def get_code_diff(github_link):
    # github_link = commit_link.split('/commit/')[0]
    all_commits = get_all_commits(github_link.split('/')[-2], github_link.split('/')[-1])

    a = 1
    # all_commits_info_in_project_template = 'curl -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/{}/{}/commits > {}'.format(
    #     github_link.split('/')[-2], github_link.split('/')[-1], 'all_commits_info_in_project.json')
    # os.system(all_commits_info_in_project_template)
    # json_result = FileUtil.load_json('all_commits_info_in_project.json')
    # a = 1
    # os.system(all_commits_info_in_project_template)
    # commit_hash = commit_link.split('/')[-1]
    # project_name = github_link.split('/')[-1]
    # user_name = github_link.split('/')[-2]
    # output_file = 'commit_diff_output.json'
    #
    # github_commit_get_api_template = 'curl -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/{}/{}/commits/{} > {}'.format(
    #     user_name, project_name, commit_hash, output_file)
    #
    # os.system(github_commit_get_api_template)

    # print(f"Commit diff saved to {output_file}")


if __name__ == '__main__':

    # json_result = FileUtil.load_json('all_commits_info_in_project.json')
    # a = 1
    optimized_commits_path = 'data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv'
    optimized_commits = pd.read_csv(optimized_commits_path)
    unique_commit_links = optimized_commits['commit_link'].unique().tolist()
    github_links = []
    for commit_link in unique_commit_links:
        github_link = commit_link.split('/commit/')[0]
        github_links.append(github_link)
    github_links = list(set(github_links))
    for github_link in github_links:
        get_code_diff(github_link)
    # for commit_link in unique_commit_links:
    #     get_code_diff(commit_link)