import datetime
import json
import os
from time import sleep
from urllib import request
from urllib.error import URLError

import arxiv


def get_json_data(url):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0',
        'Connection': 'close'
    }
    req = request.Request(url, headers=headers)
    n_tries = 5
    for _ in range(n_tries):
        try:
            res = request.urlopen(req)
            return json.loads(res.read().decode('utf-8'))
        except URLError:
            sleep(1)
    return None


def get_code_url(short_id):
    base_url = 'https://arxiv.paperswithcode.com/api/v0/papers/'
    data = get_json_data(base_url + short_id)
    if data and 'official' in data and data['official']:
        return data['official']['url']
    return None


def main():
    keywords = [
        'secure', 'security', 'privacy', 'protect', 'defense', 'attack',
        'robust', 'biometric', 'steal', 'extraction', 'membership infer',
        'federate'
    ]
    timedelta = 3
    today = datetime.datetime.utcnow().date()
    for keyword in keywords:
        dirname = keyword.replace(' ', '_')
        os.makedirs(dirname, exist_ok=True)
        exist_files = os.listdir(dirname)
        last_day = today - datetime.timedelta(days=timedelta)
        if len(exist_files) > 0:
            year, month, day = map(int,
                                   exist_files[-1].split('.')[0].split('-'))
            temp_day = datetime.date(year, month, day)
            if temp_day != today:
                last_day = temp_day
        filename = os.path.join(
            dirname, f'{today.year:04}-{today.month:02}-{today.day:02}.md')
        with open(filename, 'w', buffering=1) as fp:
            fp.write(f'# {keyword}\n\n')
            fp.write(f'## {today.month:02}-{today.day:02}\n\n')
            search = arxiv.Search(query=keyword,
                                  sort_by=arxiv.SortCriterion.SubmittedDate)
            for result in search.results():
                if result.updated.date() <= last_day:
                    break
                code_url = get_code_url(result.get_short_id())
                fp.write(f'### Title: {result.title}\n')
                fp.write(f'* Paper ID: {result.get_short_id()}\n')
                fp.write(
                    f'* Paper URL: [{result.entry_id}]({result.entry_id})\n')
                fp.write(f'* Updated Date: {result.updated.date()}\n')
                if code_url is not None:
                    fp.write(f'* Code URL: [{code_url}]({code_url})\n')
                else:
                    fp.write(f'* Code URL: null\n')
                fp.write(f'* Summary: {result.summary}\n\n')


if __name__ == '__main__':
    main()
