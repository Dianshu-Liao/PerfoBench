from NLP_filtering import Commit_Checker
import pandas as pd
import tqdm
import requests
import tiktoken


url = "http://localhost:11434/api/chat"
def llama3(messages):
    data = {
        "model": "llama3",
        "messages": messages,
        "stream": False,
        "temperature": 0,
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=data)

    return (response.json()['message']['content'])

def tokens_num(message):
    encoding = tiktoken.get_encoding("cl100k_base")  # 适用于 GPT-4、GPT-3.5-turbo 等
    tokens = encoding.encode(str(message))
    return len(tokens)


def trigger_GPT35_API_basedon_http_request(message, temperature=0):

    # url = "https://api.openai.com/v1/chat/completions"
    url = "https://openkey.cloud/v1/chat/completions"

    headers = {
        'Content-Type': 'application/json',
        # 填写OpenKEY生成的令牌/KEY，注意前面的 Bearer 要保留，并且和 KEY 中间有一个空格。
        'Authorization': 'Bearer sk-bI1WaiuEYai4cdVGAb721f63F94546BdB81fF4C80657E185'
    }

    data = {
        "model": 'gpt-3.5-turbo',
        "messages": message,
        "temperature": temperature,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    response = requests.post(url, headers=headers, json=data)
    # print("Status Code", response.status_code)
    if response.status_code != 200:
        raise ValueError("Failed to get response")
    return response.json()['choices'][0]['message']['content']


def trigger_GPT4o_API_basedon_http_request(message, temperature=0):

    # url = "https://api.openai.com/v1/chat/completions"
    url = "https://openkey.cloud/v1/chat/completions"

    headers = {
        'Content-Type': 'application/json',
        # 填写OpenKEY生成的令牌/KEY，注意前面的 Bearer 要保留，并且和 KEY 中间有一个空格。
        'Authorization': 'Bearer sk-bI1WaiuEYai4cdVGAb721f63F94546BdB81fF4C80657E185'
    }

    data = {
        "model": 'gpt-4o',
        "messages": message,
        "temperature": temperature,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    response = requests.post(url, headers=headers, json=data)
    # print("Status Code", response.status_code)
    if response.status_code != 200:
        raise ValueError("Failed to get response")
    return response.json()['choices'][0]['message']['content']

if __name__ == '__main__':

    batch_size = 100
    is_perf_unique_commits = pd.read_csv('data/is_perf_in_unique_commits.csv')
    Classifier_Prompt_Dir = 'PI_Classification_Prompt'

    for index, row in tqdm.tqdm(is_perf_unique_commits.iterrows(), total=is_perf_unique_commits.shape[0]):
        PI_Classification = row['PI_Classification']
        if pd.isna(PI_Classification):
            pass
        else:
            continue
        commit_title = row['commit_title']
        commit_description = row['commit_description']

        prompt = Commit_Checker.prompt_construction(commit_title, commit_description, Classifier_Prompt_Dir, Example_Num=4)
        # detect_result = llama3(prompt)
        prompt_token_nums = tokens_num(prompt)
        try:
            detect_result = trigger_GPT35_API_basedon_http_request(prompt)
        except:
            # detect_result = ''
            detect_result = trigger_GPT4o_API_basedon_http_request(prompt)
        is_perf_unique_commits.loc[index, 'PI_Classification'] = detect_result

        # print(detect_result)
        # a = 1
        # if index % batch_size == 0:
        #     is_perf_unique_commits.to_csv('data/is_perf_in_unique_commits.csv', index=False)
    is_perf_unique_commits.to_csv('data/is_perf_in_unique_commits.csv', index=False)
