from threading import Thread
import pymongo
from progress import progress
from data_processing import PhraseExtractor

#-------- FUNCTION DEFINITIONS ---------

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,**self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def find_ann(paper_li, ann_coll) -> str:
    #ann_coll = db['ann']
    ann_res = ann_coll.find( { "PID" : { "$in" : paper_li } } ) #find all paper ids in annotation collection that are in list
    
    #concat data into string
    this_orcid_ann = ''
    for el in ann_res:
         this_orcid_ann += el['ANN']
    #close cursor   
    ann_res.close()

    return this_orcid_ann
    

def find_mk(paper_li, mk_coll) -> str:
    #mk_coll = db['mk']
    mk_res = mk_coll.find( { "PID" : { "$in" : paper_li } } ) #find all paper ids in mesh collection that are in list
    
    #concat data into string
    this_orcid_mk = ''
    for el in mk_res:
         this_orcid_mk += el['MK']
    #close cursor     
    mk_res.close()

    return this_orcid_mk


def get_data_for_orcid(orcid_entity, ann_coll, mk_coll) -> dict:
    this_orcid = orcid_entity['ID']
    n_papers = orcid_entity['NP']
    this_orcid_papers = orcid_entity['PAPERS'].split(',') #convert string of paper ids to list
    
    
    #generates threads to find ann and mk
    this_orcid_ann = ThreadWithReturnValue(target = find_ann, args = (this_orcid_papers,ann_coll))
    this_orcid_mk = ThreadWithReturnValue(target = find_mk, args = (this_orcid_papers,mk_coll))

    #start threads
    this_orcid_ann.start()
    this_orcid_mk.start()

    #join threds and return results
    ann_res = this_orcid_ann.join()
    mk_res = this_orcid_mk.join()

    #combine returned data
    combined_data = mk_res + ann_res
    result = {'orcid':this_orcid, 'n_papers':n_papers, 'data':combined_data} #this format is required for further data processing


    return result


#------------- CONNECTION DEFINITIONS -----------

client = pymongo.MongoClient('mongodb://localhost:27017/', maxPoolSize = 1000, connect=True)
db = client['orcid'] #select database orcid
orcid_coll = db['orcid'] #select collection orcid
orcid_coll_size = db.command('collstats','orcid')['count']  #get size of collection orcid

#use different clients for different collections to speed up proces a bit
ann_client = pymongo.MongoClient('mongodb://localhost:27017/', maxPoolSize = 1000, connect=True)
ann_db = ann_client['orcid']
ann_coll = ann_db['ann']

mk_client = pymongo.MongoClient('mongodb://localhost:27017/', maxPoolSize = 1000, connect=True)
mk_db = mk_client['orcid']
mk_coll = mk_db['mk']

topic_client = pymongo.MongoClient('mongodb://localhost:27017/', maxPoolSize = 1000, connect=True)
topic_db = topic_client['topic'] 
topic_coll = db['topic'] #select collection topic to insert documents into it later



#----------- DATA PROCESSING --------------
bsize = 1000    #batch size
batches = (orcid_coll_size // bsize) + 1


for i in range(0,batches):
    k = i * bsize   #lower bound of batch
    l = k + bsize   #upper bound of batch

    subs =  'entries (' + str(k) + '-' + str(l) + ')' #current subset
    n_batches = '[' + str(i) + '/' + str(batches) + ']' #current batch/num batches

    orcid_entities = orcid_coll.find({})  #get cursor with all orcids
    entity_li = [e for e in orcid_entities[k:l]] #get orcids in this batch
    orcid_entities.close()

    threads = []
    docs = []
    # get annotations and mesh for papers of thi orcid

    for ent in entity_li:#generate threads
        th = ThreadWithReturnValue(target = get_data_for_orcid, args = (ent, ann_coll, mk_coll))
        threads.append(th)
        th.start() #start thread
    '''
    for j in range(0,len(threads)//100):
        n = j * 100
        m = n + 100
        subset = threads[n:m]
    '''
    j = 0
    #join threads to main process
    for th in threads:
        progress(j, 1000, 'retrieving data, batch ' + n_batches + ' ' + subs) #display current progress
        docs.append(th.join())
        j += 1

    print('processing data',flush = True)
    output = PhraseExtractor(docs = docs).result() #extract phrses

    log_res = topic_coll.insert_many(output)

client.close()
ann_client.close()
mk_client.close()