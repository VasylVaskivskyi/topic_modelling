import requests
import json
from math import ceil
from time import sleep

def check_dupl(data_li, el):
    dupl_li = []
    result_str = ''
    for obj in data_li:
        obj_str = obj[el].lower() + ';'
        if obj_str not in dupl_li:
            dupl_li.append(obj_str)
            result_str += obj_str
        else:
            continue

    return result_str

def get_annotations_by_papers(cursor_mark):
    link = 'https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByProvider?provider=Europe%20PMC&filter=1&format=JSON&cursorMark=' + cursor_mark + '&pageSize=8'
    resp = requests.get(link) #response
    res = resp.content.decode() #decode from bin
    data = json.loads(res) #convert to json
    next_cursor_mark = str(data['nextCursorMark']) #get next cursor mark
    ann_dict = dict()
    
    if data['articles'] == []:
        return  ann_dict, next_cursor_mark
    else:
        for paper in data['articles']:
            ann = ''
            if 'extId' in paper: #external id is primary option because it also is for data that comes with orcid
                paper_info = paper['source'] + ':' + paper['extId']
            else:
                paper_info = 'PMC:' + paper['pmcid'] #if ti is not specified use pmcid 
            ann += check_dupl(paper['annotations'], 'exact') #remove duplicated annotations
            
            ann_dict.update({paper_info:ann})
    
    
    return ann_dict, next_cursor_mark


def ann_download(start_cursor, end_cursor, suffix, dir):
    cursor_mark = start_cursor
    path_ann = dir + 'ann' + str(suffix) + '.txt'
    path_ann_cursor =  dir + 'ann_cursor' + str(suffix) + '.txt'


    while True:
        if ceil(float(cursor_mark)) == float(end_cursor):
            break
            
        ann_dict, cursor_mark = get_annotations_by_papers(cursor_mark)
        
        try:
            with open(path_ann,'a',encoding = 'utf-8') as f:
                for key,val in ann_dict.items():
                    f.write(key + '\t' + val + '\n')
                f.close()
        except PermissionError:
            sleep(1)
            with open(path_ann,'a',encoding = 'utf-8') as f:
                for key,val in ann_dict.items():
                    f.write(key + '\t' + val + '\n')
                f.close()
        
        try:    
            with open(path_ann_cursor,'a',encoding = 'utf-8') as cur:
                cur.write(cursor_mark + '\n')
                cur.close()
        except PermissionError:
            sleep(1)
            with open(path_ann,'a',encoding = 'utf-8') as f:
                for key,val in ann_dict.items():
                    f.write(key + '\t' + val + '\n')
                f.close()