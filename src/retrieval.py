import pyndri
from nltk.tokenize import RegexpTokenizer

import pandas as pd
import json
import sys
import os
import random
import argparse

import csv


from math import exp

def process_results(indri_results,index,metadata_df, metadata_pas_df, reranking_scores_df, query_id, passages=False):
    output=[]
    count=0

    #score normalization
    min=1
    max=0
    for int_document_id, score in indri_results:
        if exp(score) < min:
            min=exp(score)
        if exp(score) > max:
            max=exp(score)

    #loop throgout result and prepare output
    for int_document_id, score in indri_results:
        count+=1
        ext_document_id, _ = index.document(int_document_id)

        doc_id = ext_document_id
        sys.stderr.write("\r processed {} documents {} ".format(count, ext_document_id))
        snippet=""
        if passages == True:
            passage_metadata_row = metadata_pas_df[metadata_pas_df["paragraph_id"]==int(ext_document_id)]
            if passage_metadata_row.empty:
                sys.stderr.write("\r no passage metadata for document {} \n ".format(ext_document_id))
                continue

            doc_id=passage_metadata_row.iloc[0]["cord_uid"]
            snippet=passage_metadata_row.iloc[0]["text"]

        # common fields for documents and passages
        doc_metadata_row = metadata_df[metadata_df["cord_uid"]==doc_id]
        if doc_metadata_row.empty:
            sys.stderr.write("\r no document metadata for document {} \n ".format(ext_document_id))
            continue
        url=doc_metadata_row.iloc[0]["url"]
        title=doc_metadata_row.iloc[0]["title"]
        author=doc_metadata_row.iloc[0]["authors"]
        journal=doc_metadata_row.iloc[0]["journal"]

        #reranking
        q_candidate_id="q-"+str(query_id)+"-"+str(doc_id)
        if passages == True:
            q_candidate_id = q_candidate_id+"_"+ext_document_id
            
        bert_score=None #bert score, if not found do not take it into account
        reranking_score_row=reranking_scores_df[reranking_scores_df["query_candidate_id"]==q_candidate_id]
        if not reranking_score_row.empty:
            bert_score=reranking_score_row.iloc[0]["pos_score"]
            #sys.stderr.write("bert score for candidate {}: {} \n".format(q_candidate_id,bert_score))
            
        indri_score=(exp(score)-min)/(max-min)  # normalized indri score

        if bert_score != None:
            ranking_score=0.8*indri_score+0.2*bert_score
        else:
            ranking_score=indri_score
            
        coords = {"coord_x":random.uniform(0, 1),"coord_y":random.uniform(0, 1)}
    
        if passages == False:
            snippet=doc_metadata_row.iloc[0]["abstract"]
    

        #generate uniq doc_ids for both pas and docs
        if passages == True:
            doc_id= doc_id+"_"+ext_document_id
        
        doc ={"doc_id":doc_id, "title":title, "journal":journal,"author":author, "url":url,"text":snippet,"ranking_score":ranking_score, "indri_score":indri_score, "coordinates": coords}
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
    reranking_scores=args.reranking_scores
    
    metadata="metadata.csv_covid-19.kwrds.csv"
    passage_metadata="metadata.csv_covid-19.kwrds.paragraphs.csv"
    
    # metadata for documents
    metadata_doc=pd.read_csv(os.path.join(metadata_path,metadata))
    sys.stderr.write("metadata shape: {} \n".format(metadata_doc.shape))

    # if passages are to be retrieved instead of full documents open also metadata for passages.
    metadata_pas=pd.read_csv(os.path.join(metadata_path,passage_metadata))
    sys.stderr.write("metadata shape: {} \n".format(metadata_pas.shape))


    reranking_scores_df=pd.DataFrame(columns=["query_candidate_id","label","neg_score","pos_score"])
    # if exists, reranking-scores file
    if os.path.isfile(reranking_scores):
        reranking_scores_df=pd.read_csv(reranking_scores,dialect='excel-tab')


    rerank_csv="rerank-queries.tsv"
    of=open(rerank_csv,"w", encoding='utf-8')
    fieldnames=["question", "question_id","answer","answer_id","label"]
    wr=csv.DictWriter(of,fieldnames=fieldnames, dialect='excel-tab')
    #wr.writeheader()


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

    queries_df = pd.read_csv(queries,dialect='excel-tab')
    for index, row in queries_df.iterrows(): 
        querylc = row['query'].lower()

        sys.stderr.write("current query: {} \n.".format(querylc))
        tokens = tokenizer.tokenize(querylc)        
        tokenized_query=" ".join(tokens)

        # document level results
        results = index_doc.query(tokenized_query, results_requested=maxdocs)
        docs = process_results(results,index_doc,metadata_doc, metadata_pas, reranking_scores_df, row["id"])

        sys.stderr.write("docs retrieved, {} \n".format(len(docs)))

        for d in docs:
            wr.writerow({"question":row["query"],"question_id":row["id"],"answer":d["text"],"answer_id":d["doc_id"],"label":0}) 
        
        # document level results
        results = index_pas.query(tokenized_query, results_requested=maxdocs)
        pas = process_results(results,index_pas,metadata_doc, metadata_pas, reranking_scores_df, row["id"], passages=True)

        sys.stderr.write("passages retrieved, {} \n".format(len(docs)))

        for p in pas:
            wr.writerow({"question":row["query"],"question_id":row["id"],"answer":p["text"],"answer_id":p["doc_id"],"label":0}) 
        
        query_json={"query_id":row['id'], "task": row['task'], "query":row['query'], "docs":docs,"pas":pas}
        output.append(query_json)



    of.close()    
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
    parser.add_argument("-i", "--index-path", type=str, default='/media/nfs/multilingual/kaggle-covid19/xabi_scripts', help="output format")
    parser.add_argument("-m", "--metadata-path", type=str, default='/media/nfs/multilingual/kaggle-covid19', help="topic defining the words in the lists (only used for creating keyword related fields)")
    parser.add_argument("-r", "--reranking-scores", type=str, default='/media/nfs/multilingual/kaggle-covid19/reranking_scores.tsv', help="file containing scores from the finetuned BERT for reranking)")
    parser.add_argument("-d", "--maxdocs", type=int, default=50, help="max number of results to return (default is 50)")

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

