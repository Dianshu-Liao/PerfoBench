import pandas as pd
import os
import tqdm
from sklearn.metrics import cohen_kappa_score


def kappa_score(df, label1_keyword, label2_keyword):

    label1 = df[label1_keyword].tolist()
    label2 = df[label2_keyword].tolist()

    for i in range(len(label1)):
        label1[i] = int(label1[i])
        label2[i] = int(label2[i])

    kappa = cohen_kappa_score(label1, label2)
    return kappa


def calculate_commit_nums_and_apk_nums():
    perfobench_without_human_check = pd.read_csv('data/perfobench_without_human_check.csv')
    perfobench = pd.read_csv('data/perfobench.csv')

    perfobench_without_human_check_commit_nums = len(perfobench_without_human_check['commit_link'].unique())

    perfobench_commit_nums = len(perfobench['commit_link'].unique())
    perfobench_apk_nums = len(perfobench['apk_download_link'].unique())

    print('perfobench_without_human_check_commit_nums: {}'.format(perfobench_without_human_check_commit_nums))
    print('perfobench_commit_nums: {}'.format(perfobench_commit_nums))
    print('perfobench_apk_nums: {}'.format(perfobench_apk_nums))

def calculate_kappa_score():
    perfobench = pd.read_csv('data/perfobench_without_human_check.csv')
    kappa = kappa_score(perfobench, 'contain_perf', 'contain_perf_2')
    print('kappa:', kappa)

if __name__ == '__main__':
    # calculate_commit_nums_and_apk_nums()
    calculate_kappa_score()