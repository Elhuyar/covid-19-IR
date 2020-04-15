import pyndri
from nltk.tokenize import RegexpTokenizer

import pandas as pd
import json
import sys
import os
import random

def process_results(indri_results,metadata_df, metadata_pas_df, passages=False):
    output=[]
    count=0
    for int_document_id, score in results:
        count+=1
        sys.stderr.write("\r processed {} documents {} ".format(count, ext_document_id))
        ext_document_id, _ = index.document(int_document_id)

        doc_id = ext_document_id
        snippet=""
        if passages:
            passage_metadata_row = metadata_pas_df[metadata_pas_df["paragraph_id"]==ext_document_id]
            doc_id=passage_metadata_row.iloc[0]["cord_uid"]
            snippet=passage_metadata_row.iloc[0]["text"]

        # common fields for documents and passages
        doc_metadata_row = metadata_df[metadata_df["cord_uid"]==doc_id]
        url=doc_metadata_row.iloc[0]["url"]
        title=doc_metadata_row.iloc[0]["title"]
        author=doc_metadata_row.iloc[0]["authors"]
        journal=doc_metadata_row.iloc[0]["journal"]
        ranking_score=score
        coords = {"coord_x":random.uniform(0, 1),"coord_y":random.uniform(0, 1)}
    
        if passages == False:
            snippet=doc_metadata_row.iloc[0]["abstract"]
    
        
        doc ={"doc_id":doc_id, "title":title, "journal":journal,"author":author, "url":url,"text":snippet,"ranking_score":ranking_score,"coordinates": coords}
        output.append(doc)
        #print(ext_document_id, score)

        return output
    
##################################################
##                  Main function            #####
##                                           #####
##################################################       
def main(args):

    ## command line arguments
    queries=args.queries
    maxdocs=args.maxdocs
    metadata_path=args.metadata_path
    index_root=args.index_path
    
    metadata="metadata.csv_covid-19.kwrds.csv"
    passage_metadata="metadata.csv_covid-19.kwrds.paragraphs.csv"
    
    # metadata for documents
    metadata=pd.read_csv(os.path.join(metadata_path,metadata))
    sys.stderr.write("metadata shape: {} \n".format(metadata.shape))

    # if passages are to be retrieved instead of full documents open also metadata for passages.
    metadata_pas={}
    if retrieval_type.lower() == "pas":
        metadata_pas=pd.read_csv(os.path.join(metadata_path,metadata))

    # output format for bokeh
    output=[]
    documents=[]
    passages=[]
    #fieldnames=["doc_id","source","author", "url","title",]

    # indri
    index_doc_path=os.path.join(index_root,'BildumaIndex')
    index_pas_path=os.path.join(index_root,'BildumaParIndex')

    index_doc = pyndri.Index(index_doc_path)
    index_pas = pyndri.Index(index_pas_path)

    #query tokenizer
    tokenizer = RegexpTokenizer(r'\w+')

    queries_df = pd.read_csv(queries,dialiect='excel-tab')
    for index, row in queries_df.iterrows(): 
        querylc = row['query'].lower()

        tokens = tokenizer.tokenize(querylc)        
        tokenized_query=" ".join(tokens)

        # document level results
        results = index_doc.query(tokenized_query, results_requested=maxdocs)
        docs = process_results(results,metadata, metadata_pas)

        # document level results
        results = index_pas.query(tokenized_query, results_requested=50)
        pas = process_results(results,metadata, metadata_pas, passages=True)

        query_json={"query_id":row['id'], "task": row['task'], "query":row['query'], "docs":docs,"pas":pas}
        output.append(query_json)
        
print(json.dumps(output, indent=4, sort_keys=True))



##################################################
##              parameter parsing            #####
##################################################        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='script returns document and passage level result for a given indri collection (two indexes, docs and passages), inplemented for kaggle-covid-19 challenge.',
        epilog="type python3 -u retrieval.py -h for help",
        prog='retrieval.py' )

    parser.add_argument("queries", type=argparse.FileType('r'), help="File containing queries for document or or passage retrieval. tsv format, including one column called 'query'.")  
    parser.add_argument("-i", "--index-path", type=str, default='/mnt/nfs/multilingual/kaggle-covid19/xabi_scripts' help="output format")
    parser.add_argument("-m", "--metadata-path", type=str, default='/mnt/nfs/multilingual/kaggle-covid19', help="topic defining the words in the lists (only used for creating keyword related fields)")
    parser.add_argument("-d", "--maxdocs", type=int, default='50', help="max number of results to return (default is 50)")

    args=parser.parse_args()

    #check if test_file was provided
    if args.queries is None:
        sys.stdout.write("no queries supplied ")
        exit
        
    #if args.embeddings is None:
    #    args.embedding_update=False;
            
    sys.stderr.write(str(args).replace(', ','\n\t')+"\n")
    sys.stderr.flush()
    main(args)

