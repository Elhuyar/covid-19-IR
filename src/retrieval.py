import pyndri
from nltk.tokenize import RegexpTokenizer

import pandas as pd
import csv
import sys
import os
import random

retrieval_type="collection" #[collection| passage]
metadata_path="/mnt/nfs/multilingual/kaggle-covid19"

metadata="metadata.csv_covid-19.kwrds.csv"
passage_metadata="metadata.csv_covid-19.kwrds.paragraphs.csv"

# metadata for documents
metadata=pd.read_csv(os.path.join(metadata_path,metadata))
sys.stderr.write("data shape: {} \n".format(data.shape))

# if passages are to be retrieved instead of full documents open also metadata for passages.
metadata_pas={}
if retrieval_type.lower() == "passage":
    metadata_pas=pd.read_csv(os.path.join(metadata_path,metadata))
    sys.stderr.write("data shape: {} \n".format(data.shape))


# output format for bokeh
output=[]
#fieldnames=["doc_id","source","author", "url","title",]

# indri query    
index = pyndri.Index('./BildumaIndex')
query="hello world"
tokenizer = RegexpTokenizer(r'\w+')
querylc = query.lower()
tokens = tokenizer.tokenize(querylc)        
tokenized_query=" ".join(tokens)

results = index.query(tokenized_query, results_requested=50)
for int_document_id, score in results:
    ext_document_id, _ = index.document(int_document_id)

    doc_id = ext_document_id
    if retrieval_type.lower() == "passage":
        passage_metadata_row = metadata_pas[metadata_pas["paragraph_id"]==ext_document_id]
        doc_id=passage_mentadata_row.iloc[0]["cord_uid"]
        
    if retrieval_type.lower() == "collection":
        doc_metadata_row = metadata[metadata["cord_uid"]==ext_document_id]
        url=doc_metadata_row.iloc[0]["doc_url"]
        title=doc_metadata_row.iloc[0]["doc_url"]
        author=doc_metadata_row.iloc[0]["doc_url"]
        abstract=doc_metadata_row.iloc[0]["abstract"]
        ranking_score=score
        coords = {"coord_x":random.uniform(0, 1),"coord_y":random.uniform(0, 1)}
        
        doc ={"doc_id":doc_id, "title":title, "source":source,"author":author, "url":url,"abstract":abstract,"ranking_score":ranking_score,"coordinates": coords}
        output.append(doc)
    #print(ext_document_id, score)

json.dumps(outputindent=4, sort_keys=True)


