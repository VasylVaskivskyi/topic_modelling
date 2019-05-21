0. Get list of orcids and put into input folder. 

1. Download data using get_ann.py, get_mk.py, get_paper_for_orcid.py
Files will be downloaded into output folder.

It takes around a week to download annotations, 2-3 days to download mesh terms, and 2-3 days for orcid data

If during downloading exception happened, and downloading stopped 
you can continue from last cursor from *_cursor.txt file in output folder.
If download was iterrupted it's better to use remove_dups.py to check for duplicates in ids.
Absence of duplicates is necessary for generation of unique index in MongoDB.

2. After files were downloaded use mongo_import.py, to import downloaded data to MongoDB and generate index.

3. After downloaded files were imported to MongoDB, run generate_topics_and_import.py, to generate topics
for each orcid and import them into MongoDB