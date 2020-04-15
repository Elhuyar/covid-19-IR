import pyndri
from nltk.tokenize import RegexpTokenizer

import pandas as pd
import json
import sys
import os
import random


# arguments, should be command line parameters (e.g. argparse)
retrieval_type="document" #[document| passage]

metadata_path="/mnt/nfs/multilingual/kaggle-covid19"
index_root="/mnt/nfs/multilingual/kaggle-covid19/xabi_scripts"

metadata="metadata.csv_covid-19.kwrds.csv"
passage_metadata="metadata.csv_covid-19.kwrds.paragraphs.csv"

# metadata for documents
metadata=pd.read_csv(os.path.join(metadata_path,metadata))
sys.stderr.write("data shape: {} \n".format(data.shape))

# if passages are to be retrieved instead of full documents open also metadata for passages.
metadata_pas={}
if retrieval_type.lower() == "passage":
    metadata_pas=pd.read_csv(os.path.join(metadata_path,metadata))

# output format for bokeh
output=[]
#fieldnames=["doc_id","source","author", "url","title",]

# indri
index_path=os.path.join(index_root,'BildumaIndex')
if retrieval_type.lower() == "passage":
    index_path=os.path.join(index_root,'BildumaParIndex')

index = pyndri.Index(index_path)

query="hello world"

tokenizer = RegexpTokenizer(r'\w+')
querylc = query.lower()
tokens = tokenizer.tokenize(querylc)        
tokenized_query=" ".join(tokens)

results = index.query(tokenized_query, results_requested=50)
count=0
for int_document_id, score in results:
    sys.stderr.write("\n processed {} documents".format(count))
    ext_document_id, _ = index.document(int_document_id)

    doc_id = ext_document_id
    snippet=""
    if retrieval_type.lower() == "passage":
        passage_metadata_row = metadata_pas[metadata_pas["paragraph_id"]==ext_document_id]
        doc_id=passage_metadata_row.iloc[0]["cord_uid"]
        snippet=passage_metadata_row.iloc[0]["text"]

    # common fields for documents and passages
    doc_metadata_row = metadata[metadata["cord_uid"]==ext_document_id]
    url=doc_metadata_row.iloc[0]["url"]
    title=doc_metadata_row.iloc[0]["title"]
    author=doc_metadata_row.iloc[0]["authors"]
    journal=doc_metadata_row.iloc[0]["journal"]
    ranking_score=score
    coords = {"coord_x":random.uniform(0, 1),"coord_y":random.uniform(0, 1)}
    
    if retrieval_type.lower() == "document":
        snippet=doc_metadata_row.iloc[0]["abstract"]
    
        
    doc ={"doc_id":doc_id, "title":title, "journal":journal,"author":author, "url":url,"text":snippet,"ranking_score":ranking_score,"coordinates": coords}
    output.append(doc)
    #print(ext_document_id, score)

json.dumps(output, indent=4, sort_keys=True)


