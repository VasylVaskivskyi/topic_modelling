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

def orcid_papers_download(path, suffix, slice):
    path_orcid_data = path + 'orcid_data' + str(suffix) + '.txt'
    path_downloaded = path + 'downloaded_orcids' + str(suffix) + '.txt'
    
    batch_size = 100
    batches = (len(slice) // batch_size) + 1
    # need to use bathces because if open close files too often exception PermissionError may occur
    for i in range(0, batches):
        k = i * batch_size
        l = k + batch_size
        id_li = slice[k:l]
        result_li = []
        for j in range(0, len(id_li)):
            id = id_li[j]
            result_li.append(papers_for_orcid(id))
        
        try:
            with open(path_orcid_data, 'a', encoding = 'utf-8') as f_data:
                for result in result_li:
                    f_data.write(result[0] + '\t' + str(result[1]) + '\t' + ','.join(result[2]) + '\n')
                f_data.close()
        except PermissionError:
            sleep(1)
            with open(path_orcid_data, 'a', encoding = 'utf-8') as f_data:
                for result in result_li:
                    f_data.write(result[0] + '\t' + str(result[1]) + '\t' + ','.join(result[2]) + '\n')
                f_data.close()
        
        try:    
            with open(path_downloaded, 'a', encoding = 'utf-8') as f_d:   
                for d in id_li:
                    f_d.write(d + '\n')
                f_d.close()
        except PermissionError:
            sleep(1)
            with open(path_downloaded, 'a', encoding = 'utf-8') as f_d:   
                for d in id_li:
                    f_d.write(d + '\n')
                f_d.close()                             