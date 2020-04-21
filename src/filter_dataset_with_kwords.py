#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import json
import argparse

import csv

import string
import os
import sys
import random
import re
import collections
#from bs4 import UnicodeDammit

from sentence_splitter import SentenceSplitter, split_text_into_sentences

def main(args):
    ## command line arguments
    corpus=args.corpus
    topicTermFile=args.words
    outformat=args.outformat
    maxdocs=args.maxdocs
    topic=args.topic
    idsFile=args.ids

    
    splitter = SentenceSplitter(language='en',non_breaking_prefix_file='custom-prefixes-sent-splitter.txt')
    
    inFolder= "data-20200417"
    outFolder = "filtered"
    out_file = corpus.name+"_"+topicTermFile.name+"."+outformat
    out_file_par = corpus.name+"_"+topicTermFile.name+".paragraphs."+outformat
    out_file_sent = corpus.name+"_"+topicTermFile.name+".sentences."+outformat
    # fill words to search for
    words=collections.OrderedDict()
    for line in topicTermFile:
        if line.startswith("#") or re.match("^\s*$",line):
            continue
        fields=line.strip().split("\t")
        wrd=fields[0]
        case=""
        if len(fields)>2:
            case=fields[2]

        if not case: 
            wrd=wrd.lower()
            #sys.stderr.write("to lower - {}\n".format(wrd))

        wrdlc=wrd.replace("_"," ")
        wrdptrn=re.compile(r"\b"+re.escape(wrdlc))
        words[wrdlc]=wrdptrn
        
    topicTermFile.close()

    sys.stderr.write("Loaded keywords to select docs - {}\n".format(len(words)))

    cord_uids=collections.OrderedDict()
    for line in idsFile:
        if line.startswith("#") or re.match("^\s*$",line):
            continue
        cid=line.strip().split("\t")[0]
        cord_uids[cid]=1
    idsFile.close()
    
    sys.stderr.write("Loaded id provided by trec - {} \n".format(len(cord_uids)))#,",".join(cord_uids.keys())))
    
    output=[]
    processed={}
    metadata=csv.DictReader(corpus, dialect='excel')#delimiter='\t',  quoting=csv.QUOTE_NONE) #.drop_duplicates()
    #data=json.load(corpus)
    proces_count=0
    #sys.stderr.write("\r {a:8d} documents to process".format(a=len(list(metadata))))

    # filtered metadata file
    of=open(out_file,"w", encoding='utf-8')
    fieldnames=metadata.fieldnames
    fieldnames.append('keywords_elh')
    sys.stderr.write("fields: {}\n".format(fieldnames))
    wr=csv.DictWriter(of,fieldnames=fieldnames, dialect='excel')
    wr.writeheader()
    
    # filtered paragraph file
    of_par=open(out_file_par,"w", encoding='utf-8')
    fieldnames_par=["cord_uid","paper_id","paragraph_id","paragraph_type","text"]
    sys.stderr.write("fields for paragraph file: {}\n".format(fieldnames_par))
    wr_par=csv.DictWriter(of_par,fieldnames=fieldnames_par, dialect='excel')
    wr_par.writeheader()

    # filtered sentence file
    of_sent=open(out_file_sent,"w", encoding='utf-8')
    fieldnames_sent=["cord_uid","paper_id","paragraph_id","paragraph_type","sentence_id","text"]
    sys.stderr.write("fields for sentence file: {}\n".format(fieldnames_sent))
    wr_sent=csv.DictWriter(of_sent,fieldnames=fieldnames_sent, dialect='excel')
    wr_sent.writeheader()

    
    skipped=0
    docs_found=0
    file_problems=0
    paragraph_id=0
    no_pmc_file=0
    in_trec=0
    for row in metadata:
        proces_count+=1
        if "cord_uid" not in row or row["cord_uid"] not in cord_uids:
            sys.stderr.write("\r document {} skipped, not in the trec list".format(row["cord_uid"]))
            continue
        elif row["cord_uid"] in cord_uids:
            in_trec+=1
        
        #if proces_count > 10:
        #    sys.exit(100)
        sys.stderr.write("\r {a:8d} documents processed, {b:8d} in trec list".format(a=proces_count,b=in_trec))
        #sys.stderr.write("\n document sha {} and pmcid {} --> \n row {}\n".format(row["sha"],row["pmcid"],row))
        #we give preference to sha over pmc
        file_id=row["pmcid"]
        file_type="pmc_json"
        if row["pmcid"] == None or row["pmcid"] == '' or not os.path.isfile(os.path.join(inFolder,row["full_text_file"],row["full_text_file"],file_type,row["pmcid"]+".xml.json")):
            if not os.path.isfile(os.path.join(inFolder,row["full_text_file"],row["full_text_file"],file_type,row["pmcid"]+".xml.json")):
                no_pmc_file+=1
                sys.stderr.write("WARN: document {} has pmcid {}, but no file with that code is present, let's try with sha (pdf) \n".format(row["cord_uid"],row["pmcid"]))

            file_id=row["sha"]
            file_type="pdf_json"
            #sys.stderr.write("WARN: document {} has no sha {}\n".format(row["cord_uid"],row["sha"]))
            
            if row["sha"] == None or row["sha"] == '':
                skipped+=1
                sys.stderr.write("WARN: document {} has neither sha nor pmcid valid codes, skipping ({})\n".format(row["cord_uid"],skipped))
                continue
                             
        if file_id in processed:
            sys.stderr.write("WARN: document with file_id {} (sha or pmcid) already processed, skipping\n".format(file_id))
        else:
            processed[file_id]=1
            if row["sha"] != None and row["pmcid"] != None:
                processed[row["sha"]]=1

        extension=".json"
        if file_type == "pmc_json":
            extension=".xml.json"
            
        file_ids=file_id.split("; ")
        full_text = ""
        paragraphs=[]
        sentences=[]
        for i in file_ids:
            in_file=os.path.join(inFolder,row["full_text_file"],row["full_text_file"],file_type,i+extension)
            #out_file=os.path.join(outFolder,row["full_text_file"],row["full_text_file"],file_type,file_id+extension)

            article={}
            try: 
                with open(in_file,"r") as infile: 
                    article = json.load(infile)
                    #sys.stderr.write("current document: {}\n".format(artikulu))
            except:
                file_problems+=1
                sys.stderr.write("WARN: document with file_id {} (sha or pmcid) has problems with accessing the files, skipping\n".format(file_id))
                continue
        
            if "metadata" in article and "title" in  article["metadata"]:
                if article["metadata"]["title"] != "":
                    full_text = full_text + "\n" + article["metadata"]["title"]
                    #paragraphs
                    paragraphs.append({"cord_uid":row["cord_uid"],"paper_id":i,"paragraph_id":paragraph_id,"paragraph_type":"title","text":article["metadata"]["title"]})
                    paragraph_id+=1
                    #sentences NOTE that titles are not sentence splitted.
                    sentences.append({"cord_uid":row["cord_uid"],"paper_id":i,"paragraph_id":paragraph_id,"paragraph_type":"title","sentence_id":1,"text":article["metadata"]["title"]})
                                            
            if "abstract" in article and len(article["abstract"]) > 0:
                for abstract_node in article["abstract"]:
                    if abstract_node["text"] == None or abstract_node["text"] == "":
                        continue
                
                    full_text = full_text + "\n" + abstract_node["text"]
                    #paragraphs
                    paragraphs.append({"cord_uid":row["cord_uid"],"paper_id":i,"paragraph_id":paragraph_id,"paragraph_type":"abstract","text":abstract_node["text"]})
                    paragraph_id+=1
                    #sentences
                    sentence_id=1
                    sentence_split=splitter.split(abstract_node["text"])
                    for s in sentence_split:
                        sentences.append({"cord_uid":row["cord_uid"],"paper_id":i,"paragraph_id":paragraph_id,"paragraph_type":"abstract","sentence_id":sentence_id,"text":s})
                        sentence_id+=1
                    
            for paragraph in article["body_text"]:
                if paragraph["text"] == None or paragraph["text"] == "":
                    continue
                
                full_text=full_text + "\n" + paragraph["text"]
                #paragraphs
                paragraphs.append({"cord_uid":row["cord_uid"],"paper_id":i,"paragraph_id":paragraph_id,"paragraph_type":"body","text":paragraph["text"].replace("\n"," ")})
                paragraph_id+=1
                #sentences
                sentence_id=1
                sentence_split=splitter.split(paragraph["text"])
                for s in sentence_split:
                    sentences.append({"cord_uid":row["cord_uid"],"paper_id":i,"paragraph_id":paragraph_id,"paragraph_type":"body","sentence_id":sentence_id,"text":s})
                    sentence_id+=1
                    
        full_text = full_text.replace("“","\"").replace("&rdquor;","\"")#.replace(u"\u00AD", "")

        if ("Ã³" in full_text) or ("Ã¡" in full_text): # Ã¡ = á eta Ã³=ó
            #sys.stderr.write("current document: {}\n".format(text))
            full_text=full_text.encode("windows-1252","ignore").decode("utf-8","ignore");

        kwords_found= []
        full_textlc = full_text.lower()
        for w,ptrn in words.items():
            if re.search(ptrn,full_textlc):
                kwords_found.append(w)
                #break # for the moment all keywords are look for, 
                             
        #article["metadata"]["keywords_elh"] = kwords_found
        #sys.stderr.write("current document: {} keywords found! \n".format(row))
        if (len(kwords_found)>0):
            docs_found+=1
            row["keywords_elh"]=";".join(kwords_found)
            sys.stderr.write("current document: {} keywords found! \n".format(file_id))
            wr.writerow(row)
            #paragraphs
            for p in paragraphs:
                wr_par.writerow(p)
            #sentences
            for s in sentences:
                wr_sent.writerow(s)
                
            """
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, 'w') as outfile:
                json.dump(article, outfile)
            """

    """
    if maxdocs > 0:
        output=random.sample(output,maxdocs)
    #else:
    #    random.shuffle(output)
        
    if outformat == "json":
        with open(outfile,"w") as of:
            of.write(json.dumps(output, sort_keys=True, indent=4))
    else: #csv
        with open(outfile,"w", encoding='utf-8') as of:
            fieldnames=output[0].keys()
            sys.stderr.write("fields: {}\n".format(fieldnames))
            wr=csv.DictWriter(of,fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            wr.writeheader()
            for art in output:
                #sys.stderr.write("current document to csv: {}\n".format(art["Descripción extraída"]))

                #toprint="\t".join([art["title"],art["description"],art["body"],art["articleUrl"]])
                #print(toprint.replace)
                #print("\n")
        of.close()
    """
    of.close()
    of_par.close()
    of_sent.close()
    sys.stderr.write("\n =========================== \n SUMMARY: \n \t processed: {} \n \t keywords found in: {} \n \t skipped without code: {} \n \t file access errors: {} \n \t pmc code but not file: {} \n \t valid in trec: {} \n================== \n".format(proces_count,docs_found,skipped,file_problems,no_pmc_file, in_trec))

    

##################################################
##    Main function                          #####
##                      parameter parsing    #####
##################################################        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='',
        epilog="type python3 -u filterByKeywords.py -h for help",
        prog='dl-talaia.py' )

    parser.add_argument("corpus", type=argparse.FileType('r'), help="Corpus in csv format we want to filter")    
    parser.add_argument("-w", "--words", type=argparse.FileType('r'), help="list of words to look for in the dataset")
    parser.add_argument("-i", "--ids", type=argparse.FileType('r'), help="list of ids provided by trec organizers for each round")
    parser.add_argument("-f", "--outformat", choices=['json','csv'], default='csv', help="output format")
    parser.add_argument("-m", "--maxdocs", type=int, default='0', help="max number of documents to return")
    parser.add_argument("-t", "--topic", type=str, default='unknown', help="topic defining the words in the lists (only used for creating keyword related fields)")
    args=parser.parse_args()

    #check if test_file was provided
    if args.words is None:
        sys.stdout.write("no word list supplied ")

    #if args.embeddings is None:
    #    args.embedding_update=False;
            
    sys.stderr.write(str(args).replace(', ','\n\t')+"\n")
    sys.stderr.flush()
    main(args)
