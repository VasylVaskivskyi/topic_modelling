import requests
import json
from time import sleep
import os


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

def check_dir_exist(dir):
    if os.path.isdir(dir) == False:
        os.mkdir(dir)

path_to_orcids = '../../input/million_orcids.txt'
dir = '../../output/output_orcid/'
check_dir_exist(dir)
path_orcid_data = dir + 'orcid_data.txt'
path_downloaded = dir + 'downloaded_orcids.txt'

#orcid ids downloaded from epmc server 
ids = []
with open(path_to_orcids, 'r') as f_ids:
    for i, line in enumerate(f_ids):
        ids.append(line.strip('\n'))
    f_ids.close()



batch_size = 100
batches = (len(ids) // batch_size) + 1
# need to use bathces because if open close files too often exception PermissionError may occur
for i in range(0, batches):
    k = i * batch_size
    l = k + batch_size
    id_li = ids[k:l]
    result_li = []
    for j in range(0, len(id_li)):
        id = id_li[j]
        result_li.append(papers_for_orcid(id))
    
    with open(path_orcid_data, 'a', encoding = 'utf-8') as f_data:
        for result in result_li:
            f_data.write(result[0] + '\t' + str(result[1]) + '\t' + ','.join(result[2]) + '\n')
        f_data.close()
    
    with open(path_downloaded, 'a', encoding = 'utf-8') as f_d:   
        for d in id_li:
            f_d.write(d + '\n')
        f_d.close()