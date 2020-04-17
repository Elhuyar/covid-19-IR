#cord_uid,sha,source_x,title,doi,pmcid,pubmed_id,license,abstract,publish_time,authors,journal,Microsoft Academic Paper ID,WHO #Covidence,has_pdf_parse,has_pmc_xml_parse,full_text_file,url,keywords_elh

import csv

with open('/media/nfs/multilingual/kaggle-covid19/metadata.csv_covid-19.kwrds.csv') as tsvfile:    
    reader = csv.reader(tsvfile, dialect='excel')
    #Dont print header
    next(reader)

    for row in reader:
        dokid=row[0]
        title=row[3]
        abstract=row[8]
        print("<DOC>")
        print("<DOCID>"+dokid+"</DOCID>")
        print("<DOCNO>"+dokid+"</DOCNO>")
        print("<TEXT>\n"+title+"\n"+abstract+"\n</TEXT>")
        print("</DOC>")
