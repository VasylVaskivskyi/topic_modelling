import pymongo
from  subprocess import run, PIPE


def import_to_mongo(mongo_dir, data_path, db_name, coll_name, header_names_types):
    arguments_import = '--db ' + db_name + ' --collection ' + coll_name + ' --type tsv --file ' + data_path + ' --fields ' + header_names_types + ' --columnsHaveTypes'
    cmd_import = 'cmd /c "' + mongo_dir + 'mongoimport.exe" ' + arguments_import
    run(cmd_import, stdout = PIPE)


path_to_mongo_dir = 'C:/Program Files/MongoDB/Server/4.0/bin/' #DIRECTORY
orcids = './output/orcid_data.txt'
ann = './output/ann.txt'
mk = './output/mk.txt'

#ID - ORCID id, NP - number of papers, PAPERS - list of papers in format SOURCE:ID
#PID - paper id, ANN - annotation, MK - MeSH terms and keywords
#do not put spaces between comas in header_names_types
import_to_mongo(path_to_mongo_dir, orcids, 'orcid', 'orcid', 'ID.string(),NP.int32(),PAPERS.string()') 
import_to_mongo(path_to_mongo_dir, ann, 'orcid', 'ann', 'PID.string(),ANN.string()')
import_to_mongo(path_to_mongo_dir, mk, 'orcid', 'mk', 'PID.string(),MK.string()')



client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['orcid']


db.orcid.create_index([('ID', pymongo.ASCENDING)], unique = True, name = 'ID_i')
db.ann.create_index([('PID', pymongo.ASCENDING)], unique = True, name = 'PID_i')
db.mk.create_index([('PID', pymongo.ASCENDING)], unique = True, name = 'PID_i')

