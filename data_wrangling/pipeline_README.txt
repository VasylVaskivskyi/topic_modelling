0. Get list of orcids and put into input folder. 
Install python library nltk, run in python nltk.download() and download WordNet library under Corpora tab

1. To download data you can use multiprocess scripts or single process in folder dowloaders
SINGLE PROCESS: get_ann.py, get_mk.py, get_paper_for_orcid.py 
MULTIPROCESS: orcid_papers_download_control.py, ann_download_control.py
You can run the manually, using run.bat, or run_download.py

Files will be downloaded into output folder into separate folders.

For a single process scripts tt takes around a week to download annotations, 
1-2 days to download mesh terms, and 2-3 days for orcid data.

For multiprocess scripts 8 times less, except for MK, because I cannot use cursor.

If during downloading exception happened, and downloading stopped 
you can continue from last cursor from *_cursor.txt file in output folder.

2. Concatenate files inside output folders using concat_files.py. Delete the rest.

3. Use mongo_import.py, to import downloaded data to MongoDB and generate index.

4. If MongoDb cannot generate index, that means there are duplicates in the data. Use remove_dups.py to remove duplicates.

5. After downloaded files were imported to MongoDB, run generate_topics_and_import.py, to generate topics
for each orcid and import them into MongoDB collection 'topic'.