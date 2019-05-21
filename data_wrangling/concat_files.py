import shutil

def concat_files(dir, file_name):
    with open(dir + file_name + '0', 'wb') as outfile:
        for filename in glob.glob('*.txt'):
            if filename == outfilename:
                # don't want to copy the output into the output
                continue
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)