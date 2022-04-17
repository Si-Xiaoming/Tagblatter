import json
import os
from datetime import datetime
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
        except URLError as e:
            sleep(1)
    raise e


def get_code_url(short_id):
    base_url = 'https://arxiv.paperswithcode.com/api/v0/papers/'
    data = get_json_data(base_url + short_id)
    if 'official' in data and data['official']:
        return data['official']['url']
    return None


def main():
    keywords = ['robust', 'clip']
    cur_time = datetime.utcnow()
    for keyword in keywords:
        dirname = keyword.replace(' ', '_')
        os.makedirs(dirname, exist_ok=True)
        filename = os.path.join(dirname,
                                f'{cur_time.year:04}-{cur_time.month:02}.md')
        if os.path.exists(filename):
            with open(filename, 'r') as fp:
                lines = fp.readlines()
        else:
            lines = [f'# {keyword}\n', '\n']
        with open(filename, 'w') as fp:
            lines.insert(2, f'## {cur_time.month:02}-{cur_time.day:02}\n\n')
            search = arxiv.Search(query=keyword,
                                  max_results=3,
                                  sort_by=arxiv.SortCriterion.SubmittedDate)
            for result in search.results():
                code_url = get_code_url(result.get_short_id())
                content = ''
                content += f'### Title: {result.title}\n'
                content += f'* Paper ID: {result.get_short_id()}\n'
                content += f'* Paper URL: [{result.entry_id}]({result.entry_id})\n'
                content += f'* Updated Date: {result.updated}\n'
                if code_url is not None:
                    content += f'* Code URL: [{code_url}]({code_url})\n'
                else:
                    content += f'* Code URL: null\n'
                content += f'* Summary: {result.summary}\n\n'
                lines.insert(3, content)
            fp.writelines(lines)


if __name__ == '__main__':
    main()