from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import csv
from nltk.tokenize import RegexpTokenizer
import joblib
from nltk.corpus import stopwords
import string

import sys

tokenizer = RegexpTokenizer(r'\w+') 


#print(stopwords_english)
passages=True

in_file='metadata.csv_covid-19.kwrds.csv'
if passages:
    in_file='metadata.csv_covid-19.kwrds.paragraphs.csv'

with open(in_file) as tsvfile:    
    reader = csv.DictReader(tsvfile, dialect='excel')

    out_file = in_file+".tfidf-coords.csv"
    of=open(out_file,"w", encoding='utf-8')
    fieldnames=reader.fieldnames
    fieldnames.append('tfidf_coord_x')
    fieldnames.append('tfidf_coord_y')
    sys.stderr.write("fields: {}\n".format(fieldnames))
    wr=csv.DictWriter(of,fieldnames=fieldnames, dialect='excel')
    wr.writeheader()
    
    texts=[]
    ids={}
    kats=[]
    titles={}
    abstracts={}
    count=0
    output=[]
    for row in reader:
        sys.stderr.write("\r {} rows processed".format(count))
        dokid=""
        text=""
        if passages :
            dokid=row['paragraph_id']
            text=row['text']
        else:
            dokid=row['cord_uid']    
            text=row['title']+" "+row['abstract']
        ##print(dokid+"\t"+title+"\t"+abstract)        
        #text=title+" "+abstract


        tokens = tokenizer.tokenize(text)
        tokenak=[]
        for tok in tokens:
            #filter non alphanumeric tokens and stop words
            if not (tok in string.punctuation) and not(tok.isnumeric()) and not(tok.lower() in stopwords.words('english')) and (len(tok) > 1) :
                tokenak.append(tok)
        tokenized_text=" ".join(tokenak)
        #add tokenized document
        #print(tokenized_text)
        tokenized_text=tokenized_text.lower()
        #texts list
        texts.append(tokenized_text)
        #Dokids list
        ids[dokid]=count
        count+=1
        #Titles list
        #titles[str(dokid)]=title
        #Abs list
        #abstracts[str(dokid)]=abstract
        output.append(row)

    #Generate tfidf model
    vectorizer = TfidfVectorizer(min_df=2,max_df=0.6,norm="l2",max_features=10000)
    vecfit = vectorizer.fit(texts)
    vec_trans = vecfit.transform(texts)

    
    #Dimension reduction
    tsne_model = TSNE(n_components=2, verbose=1, random_state=0)
    svd = TruncatedSVD(n_components=50, random_state=0)
    svd_tfidf = svd.fit_transform(vec_trans)
    tsne_tfidf = tsne_model.fit_transform(svd_tfidf)
    #for i in vec_trans.toarray():
    #    print(i)
    for row in output:
        dokid='cord_uid'
        if passages:
            dokid='paragraph_id'
 
        row['tfidf_coord_x']=tsne_tfidf[ids[row[dokid]]][0]
        row['tfidf_coord_y']=tsne_tfidf[ids[row[dokid]]][1]
        
        wr.writerow(row)

    of.close()
#    joblib.dump(titles, 'covid_Titles.pkl')
#    joblib.dump(tsne_tfidf, 'covid_Tfidf_tsne.pkl')
#    joblib.dump(kats, 'covid_Names.pkl')
#    joblib.dump(vecfit, 'covid_Tfidfmodel.pkl')
#    joblib.dump(vec_trans, 'covid_Tfidf.pkl')
#    joblib.dump(abstracts, 'covid_abs.pkl')
    

