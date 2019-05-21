import requests
import json

path_mk = './output/mk.txt'
path_mk_cursor = './output/mk_cursor.txt'


def get_mk(cursor_mark):
    link = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=*&resultType=core&cursorMark=' + cursor_mark + '&pageSize=1000&format=json'
    resp = requests.get(link) #response
    res = resp.content.decode() #decode from bin
    data = json.loads(res) #convert to json
    mk_dict = dict() #init dictionary for collecting data
    next_cursor_mark = str(data['nextCursorMark']) #get next cursor mark

    if 'resultList' not in data:
        return mk_dict, cursor_mark, next_cursor_mark
    for entry in data['resultList']['result']:
        keywords = ''
        paper_info = str(entry['source']) + ':' + str(entry['id'])

        if 'meshHeadingList' in entry:
            for i in range(0, len(entry['meshHeadingList']['meshHeading'])):
                keywords += entry['meshHeadingList']['meshHeading'][i]['descriptorName'] + ';'

        if 'keywordList' in entry:
            entry_li = entry['keywordList']['keyword']
            if None in entry_li:
                entry_li = [el for el in entry_li if el is not None]
            keywords += ';'.join(entry_li) + ';'

        mk_dict.update({paper_info:keywords})

    return mk_dict, cursor_mark, next_cursor_mark


cursor_mark = ''
next_cursor_mark = '*'

while next_cursor_mark != cursor_mark:

    mk_dict, cursor_mark, next_cursor_mark = get_mk(next_cursor_mark)

    with open(path_mk, 'a', encoding = 'utf-8') as f:
        for key,val in mk_dict.items():
            f.write(key + '\t' + val + '\n')
        f.close()
    with open(path_mk_cursor, 'a', encoding = 'utf-8') as cur:
        cur.write(cursor_mark + '\n')
        cur.close()