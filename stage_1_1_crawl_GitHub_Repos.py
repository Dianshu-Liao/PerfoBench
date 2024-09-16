import time

import requests
from bs4 import BeautifulSoup
import csv
import tqdm
import os
import pandas as pd
import re


def get_categories_link():
    response = requests.get("https://f-droid.org/en/packages/")
    response.raise_for_status()  # 如果请求有问题则抛出异常

    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.content, 'html.parser')
    # 查找所有符合条件的a标签
    a_tags = soup.select('div.post-content p a')
    # 提取所有a标签的href属性
    links = [a.get('href') for a in a_tags]
    links = ['https://f-droid.org' + link for link in links]

    return links


def get_list_by_categories(category):
    # 获取类别名称
    print(f'category link: {category}')
    category_name = re.search(r'categories/([^/]+)/', category).group(1)
    print(f'Category name: {category_name}')

    next_page_link = category
    app_list = []
    while next_page_link != None:
        # 获取网页内容
        response = requests.get(next_page_link)
        html_content = response.text
        # print(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        # 获取下一页链接
        next_page = soup.find('a', text='Older Posts â')
        if next_page != None:
            next_page_link = 'https://f-droid.org' + next_page.get('href')
        else:
            next_page_link = None
            print("No Next Page")
        # 获取本页所有app的link&name
        news_content_div = soup.find('div', id='news-content')

        if news_content_div:
            h3s = news_content_div.find_all('h3')
            for h3 in h3s:
                a_tag = h3.find('a')
                if a_tag:
                    href = a_tag.get('href')
                    text = a_tag.get_text()
                    print(f'href: {href}')
                    app_list.append(('https://f-droid.org' + href, text))

    return category_name, app_list


def get_git_link_by_app(app):
    app_link, app_name = app
    response = requests.get(app_link)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    # 查找所有文本内容为'Source Code'的a标签
    source_code_link = soup.find('a', string='Source Code')['href']
    print(f'{app_name} git url: {source_code_link}')
    return (app_name, source_code_link, app_link)


def save_as_csv(FDdata_directory, category, app_list):
    # CSV文件的名称
    csv_file = f'{FDdata_directory}/{category}.csv'
    # csv_file = f'./data/GitHub_Repo_Data/FDdata/{category}.csv'

    # 打开一个文件用于写入
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['AppName', 'gitLink', 'FDstoreLink'])

        for app in app_list:
            writer.writerow(app)

    print(f'{category} 已保存到 {csv_file}')


def get_FDdata(FDdata_directory):
    all_apps_num = 0
    categories_link = get_categories_link()
    for category_link in categories_link:

        category, app_list = get_list_by_categories(category_link)
        all_apps_num += len(app_list)
        csv_file_path = f'{FDdata_directory}/{category}.csv'
        if os.path.exists(csv_file_path):
            continue
        print(len(app_list))
        all_apps_num += len(app_list)
        all_git_links = []
        for app in tqdm.tqdm(app_list):
            try:
                git_links_by_app = get_git_link_by_app(app)
                all_git_links.append(git_links_by_app)
                time.sleep(10)
            except:
                pass
        save_as_csv(FDdata_directory, category, all_git_links)
    print(all_apps_num)


if __name__ == "__main__":

    # 设定文件夹路径
    FDdata_directory = './data/GitHub_Repo_Data/FDdata'
    get_FDdata(FDdata_directory)
