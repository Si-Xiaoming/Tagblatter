import datetime
import os
import random
import time
from turtle import pd
from unicodedata import category

import arxiv
import requests

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44',
    'Connection': 'close'
}


def get_code_url(short_id):
    base_url = 'https://arxiv.paperswithcode.com/api/v0/repos-and-datasets/'
    time.sleep(random.random())
    data = requests.get(base_url + short_id, headers=headers).json()
    if data and 'code' in data:
        if data['code'] and 'official' in data['code']:
            if data['code']['official'] and 'url' in data['code']['official']:
                return data['code']['official']['url']
    return None


def main():
    keywords = [
        'secure', 'security', 'privacy', 'protect', 'defense', 'attack',
        'robust', 'biometric', 'steal', 'extraction', 'membership infer',
        'federate', 'fair', 'interpretability', 'exlainability', 'watermark'
    ]
    categories = {'cs.CV', 'cs.CL', 'cs.CR', 'cs.AI', 'cs.LG'}
    timedelta = 3
    today = datetime.datetime.utcnow().date()
    fp_readme = open('README.md', 'w')
    fp_readme.write(f'# arxiv-daily\n')
    fp_readme.write(f'updated on {today}\n')
    fp_readme.write(f'| keyword | count | update_date | last_update_date |\n')
    fp_readme.write(f'| - | - | - | - |\n')
    for keyword in keywords:
        dirname = keyword.replace(' ', '_')
        os.makedirs(dirname, exist_ok=True)
        exist_files = os.listdir(dirname)
        last_day = today - datetime.timedelta(days=timedelta)
        if len(exist_files) > 0:
            year, month, day = map(
                int,
                sorted(exist_files)[-1].split('.')[0].split('-'))
            last_day = min(last_day, datetime.date(year, month, day))
        search = arxiv.Search(query=keyword,
                              sort_by=arxiv.SortCriterion.SubmittedDate)
        cnt = 0
        for result in search.results():
            if result.updated.date() <= last_day:
                print(last_day, today, keyword, cnt)
                fp_readme.write(f'| {keyword} | {cnt} | {today} | {last_day} |\n')
                break
            if len(set(result.categories) & categories) == 0:
                continue
            cnt += 1
            temp_day = result.updated.date()
            filename = os.path.join(
                dirname,
                f'{temp_day.year:04}-{temp_day.month:02}-{temp_day.day:02}.md')
            with open(filename, 'a+', buffering=1) as fp:
                code_url = get_code_url(result.get_short_id())
                fp.write(f'### Title: {result.title}\n')
                fp.write(f'* Paper ID: {result.get_short_id()}\n')
                fp.write(
                    f'* Paper URL: [{result.entry_id}]({result.entry_id})\n')
                fp.write(f'* Updated Date: {result.updated.date()}\n')
                fp.write(f'* Categories: {result.categories}\n')
                if code_url is not None:
                    fp.write(f'* Code URL: [{code_url}]({code_url})\n')
                else:
                    fp.write(f'* Code URL: null\n')
                fp.write(f'* Summary: {result.summary}\n\n')
    fp_readme.close()


if __name__ == '__main__':
    main()
