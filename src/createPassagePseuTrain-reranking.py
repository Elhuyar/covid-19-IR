import csv
import random


titles={}
absts={}


with open('/mnt/nfs/multilingual/kaggle-covid19/metadata.csv') as tsvfile:    
    reader = csv.reader(tsvfile, delimiter=',',quotechar='"')
    #Don't print header
    next(reader)
    for row in reader:
        dokid=row[0]
        title=row[3]
        abstract=row[8]
        if abstract.strip() != "" and title.strip() != "": 
            titles[dokid]=title
            absts[dokid]=abstract


for dokid in titles:
    # positive examples
    print(titles[dokid]+"\t"+dokid+"\t"+absts[dokid]+"\t"+dokid+"\t1")

    #negative examples (1:10 positve:negative ratio)
    for i in range(10):
        dokid2=random.choice(list(absts.keys()))
        print(titles[dokid]+"\t"+dokid+"\t"+absts[dokid2]+"\t"+dokid2+"\t0")
