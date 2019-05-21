from multiprocessing import Process
import shutil
import os
from get_papers_for_orcid import get_by_cursormark, papers_for_orcid, orcid_papers_download

def check_dir_exist(dir):
    if os.path.isdir(dir) == False:
        os.mkdir(dir)
        
def run_download(dir, path_to_orcid_list):
    ids = []
    with open(path_to_orcid_list, 'r') as f_ids:
        for i, line in enumerate(f_ids):
            ids.append(line.strip('\n'))
        f_ids.close()
    
    slice_size = (len(ids) // 8) + 1
    proc_list = []
    for i in range(0, 8):
        k = i * slice_size
        l = k + slice_size
        p = Process(target = orcid_papers_download, args = (dir, i, ids[k:l]))
        proc_list.append(p)
        p.start()
        
    for p in proc_list:
        p.join()

def concat_files(dir):
    with open(dir + 'orcid_data0', 'wb') as outfile:
        for filename in glob.glob('*.txt'):
            if filename == outfilename:
                # don't want to copy the output into the output
                continue
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)
    with open(dir + 'downloaded_orcids0', 'wb') as outfile:
        for filename in glob.glob('*.txt'):
            if filename == outfilename:
                # don't want to copy the output into the output
                continue
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)



path_to_orcid_list = '../../input/million_orcids.txt'
dir = '../../output/output_orcid/'

if __name__ == "__main__":
    check_dir_exist(dir)
    run_download(dir, path_to_orcid_list)
    #concat_files(dir)


