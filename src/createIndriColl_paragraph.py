import csv

#cord_uid,paper_id,paragraph_id,paragraph_type,text
with open('/media/nfs/multilingual/kaggle-covid19/metadata.csv_covid-19.kwrds.paragraphs.csv') as tsvfile:    
    reader = csv.reader(tsvfile, dialect='excel')
    #Dont print header
    next(reader)

    for row in reader:
        corid=row[0]
        dokid=row[1]
        par_id=row[2]
        text_type=row[3]
        par_text=row[4]

        if text_type == "body":
            print("<DOC>")
            print("<DOCID>"+par_id+"</DOCID>")
            print("<DOCNO>"+par_id+"</DOCNO>")
            print("<TEXT>\n"+par_text+"\n</TEXT>")
            print("</DOC>")
            
