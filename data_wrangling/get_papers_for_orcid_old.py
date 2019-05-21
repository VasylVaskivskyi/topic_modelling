import requests
import json
from time import sleep
import os

path_to_orcids = './input/million_orcids.txt'
path_orcid_data = './output/orcid_data.txt'
path_downloaded = './output/downloaded_orcids.txt'

#orcid ids downloaded from epmc server 
ids = []
with open(path_to_orcids, 'r') as f_ids:
    for i, line in enumerate(f_ids):
        ids.append(line.strip('\n'))
    f_ids.close()


def get_by_cursormark(orcid, cursor_mark):
    link = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTHORID%3A' + orcid + '&resultType=idlist&cursorMark=' + cursor_mark + '&pageSize=1000&format=json'
    resp = requests.get(link)
    res = resp.content.decode()
    data = json.loads(res)
    next_cursor_mark = str(data['nextCursorMark'])
    paper_info_li = []

    for entry in data['resultList']['result']:
        paper_info = str(entry['source']) + ':' + str(entry['id'])
        paper_info_li.append(paper_info)

    return paper_info_li, cursor_mark, next_cursor_mark


def papers_for_orcid(orcid):
    link = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTHORID%3A' + orcid + '&resultType=idlist&cursorMark=*&pageSize=1000&format=json'
    resp = requests.get(link)
    res = resp.content.decode()
    if res == [] :
        return [orcid, '0', []]
    data = json.loads(res)
    paper_info_li = []
    if 'resultList' not in data:
        return [orcid, '0', []]

    for entry in data['resultList']['result']:
        paper_info = str(entry['source']) + ':' + str(entry['id'])
        paper_info_li.append(paper_info)

    if data['hitCount'] > 1000: #if nuber of articles is more than 1000 use cursor mark
        cursor_mark = '*'
        next_cursor_mark = data['nextCursorMark']
        longer_paper_li = []
        while True:
            more_paper_info_li, cursor_mark, next_cursor_mark = get_by_cursormark(orcid, next_cursor_mark)
            longer_paper_li.extend(more_paper_info_li)
            if cursor_mark == next_cursor_mark:
                break
        paper_info_li.extend(longer_paper_li)
        result = [orcid, len(paper_info_li), paper_info_li]
    else:
        result = [orcid, len(paper_info_li), paper_info_li]
    return result


for i in range(0,len(ids)):
    id = ids[i]

    #if file opening and closing happens too fast permission error may occur, that's why opening and closing separated
    try:
        f_data = open(path_orcid_data, 'a', encoding = 'utf-8')
        f_d = open(path_downloaded, 'a', encoding = 'utf-8')
    except PermissionError:
        sleep(5)
        try:
            f_data = open(path_orcid_data, 'a', encoding = 'utf-8')
            f_d = open(path_downloaded, 'a', encoding = 'utf-8')
        except PermissionError:
            os.chmod(path_orcid_data, 7777)
            os.chmod(path_downloaded, 7777)
            f_data = open(path_orcid_data, 'a', encoding = 'utf-8')
            f_d = open(path_downloaded, 'a', encoding = 'utf-8')


    result = papers_for_orcid(id)

    f_data.write(result[0] + '\t' + str(result[1]) + '\t' + ','.join(result[2]) + '\n')
    f_d.write(id + '\n')
    f_data.close()
    f_d.close()