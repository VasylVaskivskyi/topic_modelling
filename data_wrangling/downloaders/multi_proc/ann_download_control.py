from multiprocessing import Process
import os 
from get_ann import check_dupl,get_annotations_by_papers, ann_download

def check_dir_exist(dir):
    if os.path.isdir(dir) == False:
        os.mkdir(dir)

def run_download(dir, slices):
    proc_list = []
    for key, val in slices.items():
        p = Process(target = ann_download, args = (val[0],val[1], key, dir))
        proc_list.append(p)
        p.start()
        
    for p in proc_list:
        p.join()

dir  = '../../output/output_ann/'
slices = {0:('0.0','500'),1 :('500','100'), 2:('100','50'), 3:('50','30'), 4:('30','10'),5:('10','5'),7:('5','-1')} #the lesser the cursor number the more data to download

if __name__ == "__main__":
    check_dir_exist(dir)
    run_download(dir, slices)
    