import shutil
import os

def concat_files(dir):
    if not dir.endswith('/'):
        dir += '/'
    file_li = os.listdir(dir) #list files in the directory
    
    output_files = [] 
    for f in file_li: #find out output file names
        if f[:-4].endswith('0'):
            output_files.append(f[:-5])
    
    for of in output_files: #concatenate all the files to output files
        with open(dir + of + '.txt', 'wb') as out_f:
            for f in file_li:
                if f[:-5] == of:
                    with open(dir + f, 'rb') as in_f:
                        shutil.copyfileobj(in_f, out_f)
                    in_f.close
        out_f.close()
        