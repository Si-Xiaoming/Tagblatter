import datetime
import os
import random
import time

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
    timedelta = 4
    now = datetime.datetime.utcnow()
    fp_readme = open('README.md', 'w')
    fp_readme.write(f'# arxiv-daily\n')
    fp_readme.write(f'updated on {now}\n')
    fp_readme.write(f'| keyword | count | update_time | last_update_time |\n')
    fp_readme.write(f'| - | - | - | - |\n')
    for keyword in keywords:
        dirname = keyword.replace(' ', '_')
        os.makedirs(dirname, exist_ok=True)
        exist_files = os.listdir(dirname)
        last_update_time = now - datetime.timedelta(days=timedelta)
        if len(exist_files) > 0:
            last_update_time = min(
                last_update_time,
                datetime.datetime.strptime(
                    sorted(exist_files)[-1].split('.')[0],
                    '%Y-%m-%d-%H-%M-%S'))
        search = arxiv.Search(query=keyword,
                              sort_by=arxiv.SortCriterion.SubmittedDate)
        cnt = 0
        filename = None
        for result in search.results():
            update_time = result.updated.replace(tzinfo=None)
            if update_time <= last_update_time:
                fp_readme.write(
                    f'| {keyword} | {cnt} | {now} | {update_time} |\n')
                break
            if len(set(result.categories) & categories) == 0:
                continue
            cnt += 1
            if filename is None:
                filename = os.path.join(
                    dirname,
                    f'{datetime.datetime.strftime(update_time,                                                   "%Y-%m-%d-%H-%M-%S")}.md'
                )
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
