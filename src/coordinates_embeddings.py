from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import csv
from nltk.tokenize import RegexpTokenizer
import joblib
from nltk.corpus import stopwords
import string


tokenizer = RegexpTokenizer(r'\w+') 


#print(stopwords_english)


with open('MetadataFiltered.csv') as tsvfile:    
    reader = csv.reader(tsvfile, delimiter='\t',quotechar='"')
    #Dont print header
    next(reader)

    texts=[]
    kats=[]
    titles={}
    abstracts={}
    for row in reader:
        
        dokid=row[0]
        title=row[1]
        abstract=row[2]
        ##print(dokid+"\t"+title+"\t"+abstract)        
        text=title+" "+abstract


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
        kats.append(dokid)
        #Titles list
        titles[str(dokid)]=title
        #Abs list
        abstracts[str(dokid)]=abstract

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
    
    joblib.dump(titles, 'covid_Titles.pkl')
    joblib.dump(tsne_tfidf, 'covid_Tfidf_tsne.pkl')
    joblib.dump(kats, 'covid_Names.pkl')
    joblib.dump(vecfit, 'covid_Tfidfmodel.pkl')
    joblib.dump(vec_trans, 'covid_Tfidf.pkl')
    joblib.dump(abstracts, 'covid_abs.pkl')
    
                                         
