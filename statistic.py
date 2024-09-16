import pandas as pd
import tqdm

def commit_num(df_path):
    df = pd.read_csv(df_path)
    unique_commit_links = df['commit_link'].unique().tolist()
    print('unique commit links: {}'.format(len(unique_commit_links)))

if __name__ == '__main__':
    # # all commits num
    commit_num('data/Saved_Commit_Data.csv')

    # commits after heuristics filter
    commit_num('data/Saved_Commit_Data_After_First_Filter.csv')

    # commits after NLP filter
    commit_num('data/Saved_Commit_Data_After_Second_Filter.csv')

    # commits after PI classification
    commit_num('data/Saved_Commit_Data_After_Third_Filter_with_PI_classification_format.csv')

    commit_num('data/perfobench_without_human_check.csv')

    commit_num('data/perfobench.csv')

