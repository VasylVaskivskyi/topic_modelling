import pandas
import os

input_path = 'orcid_data.txt'

def remove_duplicates(file_path):
    new_name = file_path.replace('.txt','_processed.txt')
    print('reading file')
    file = pandas.read_csv(file_path, sep = '\t', dtype = str, header = None, low_memory = True, engine = 'c', encoding = 'utf-8', memory_map = True)
    print('removing duplicates')
    file.drop_duplicates(subset = 0,keep = 'last', inplace = True)
    print('writing file')
    file.to_csv(new_name, sep = '\t', header = False, index = False, encoding = 'utf-8')
    print('processed successfully file at: ', file_path)
    print('output file at: ', new_name)
    return


remove_duplicates(input_path)