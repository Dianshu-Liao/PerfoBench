import pandas as pd
import tqdm
from file_util import FileUtil
import os
import tiktoken
import re
import requests


def remove_non_english_titles(df):
    # Drop rows where both commit_title and commit_description are NaN
    df = df.dropna(subset=['commit_title', 'commit_description'], how='all')

    # Function to check if the string contains only ASCII characters
    def is_english(text):
        return bool(re.match(r'^[\x00-\x7F]+$', text))

    # Filter out rows where commit_title contains non-English characters and commit_description contains non-English characters
    df_filtered = df[df['commit_title'].apply(lambda x: is_english(str(x)) if pd.notnull(x) else False)]

    # Filter commit_description: keep if NaN or if English
    df_filtered = df_filtered[
        df_filtered['commit_description'].apply(lambda x: is_english(str(x)) if pd.notnull(x) else True)]

    return df_filtered


def remove_useless_rows(df):
    df = df.dropna(subset=['commit_title', 'commit_description'], how='all')

    df = remove_non_english_titles(df)

    useless_titles = ['Update README.md', 'refactoring', 'add new screenshots', 'remove old screenshots',
                      'update icon', 'initial commit', 'Reformat', 'Fix compilation', 'formatting', 'added',
                      'update f-droid metadata', 'add todos', 'remove dead code', 'Dutch',
                      'adding a new string for Go to date',
                      'Move source files to a more standard location', 'Refactor',
                      'replace last occurrences of the old package id',
                      'update links', 'update dependencies', 'Updated changelog.', 'Update changelog.',
                      'Updated the changelog.',
                      'updating commons', 'Update imports', 'Update libs', 'Update genius scan sdk',
                      'refactor: Update files Header',
                      'Update', 'Merge master', 'Cleanup.', '...', 'new version', 'init', 'Release', 'Bug fixes',
                      'Year++', 'fix errors', 'Bump version', 'no message', 'Fixes', 'Update README', 'Refactoring',
                      'Updates', 'Updated texts', 'Initial import']
    len_useless_titles = len(useless_titles)
    # Convert all useless titles to lowercase
    useless_titles = [title.lower() for title in useless_titles]

    # Filter the DataFrame
    df_filtered = df[~((df['commit_title'].str.lower().isin(useless_titles)) & (df['commit_description'].isna()))]


    # df_filtered = df[~((df['commit_title'].isin(useless_titles)) & (df['commit_description'].isna()))]

    # 正则表达式 version + number (for example, version 1.6, version 0.4.2)
    version_number = re.compile(r'version\s+\d+(\.\d+)*')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(version_number.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(version_number.search(x))))]

    # 正则表达式 Merge pull request #number from user (for example, Merge pull request #205 from weblate/weblate-you-apps-connect-you)
    merge_pull_request = re.compile(r'Merge pull request #\d+ from \w+/\w+')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(merge_pull_request.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(merge_pull_request.search(x))))]

    # 正则表达式Merge branch 'branch_name' (for example, Merge branch 'master')
    merge_branch = re.compile(r'Merge branch \'\w+\'')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(merge_branch.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(merge_branch.search(x))))]

    # 正则表达式version number (for example, v1.6.0, v0.4.2)
    version_number_v = re.compile(r'v\d+(\.\d+)*')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(version_number_v.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(version_number_v.search(x))))]

    # 正则表达式纯数字(for example, 1.1.2, 1.2.3, 2.5.0.2)
    version_number_pure = re.compile(r'\d+(\.\d+)*')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(version_number_pure.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(version_number_pure.search(x))))]


    # 正则表达式Release version number (for example, Release 1.6.0, Release 0.4.2)
    release_version_number = re.compile(r'Release \d+(\.\d+)*')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(release_version_number.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(release_version_number.search(x))))]

    # 正则表达式Update Kotlin to version number (for example, Update Kotlin to version 1.6.0)
    update_kotlin = re.compile(r'Update Kotlin to version \d+(\.\d+)*')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(update_kotlin.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(update_kotlin.search(x))))]

    # 正则表达式added xxx files (for example, added build.xml files)中间xxx只代表一个单词
    added_files = re.compile(r'added [\w.]+ files')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(added_files.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(added_files.search(x))))]

    # 正则表达式remove xxx files (for example, remove .DS_Store files)中间xxx只代表一个单词
    remove_files = re.compile(r'remove [\w.]+ files')
    # filtered_rows = df_filtered[df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
    #     lambda x: bool(remove_files.search(x)))]
    df_filtered = df_filtered[~(df_filtered['commit_description'].isna() & df_filtered['commit_title'].apply(
        lambda x: bool(remove_files.search(x))))]

    return df_filtered


if __name__ == '__main__':


    df = pd.read_csv('data/Saved_Commit_Data.csv')
    df = remove_useless_rows(df)
    df.to_csv('data/Saved_Commit_Data_After_First_Filter.csv', index=False)