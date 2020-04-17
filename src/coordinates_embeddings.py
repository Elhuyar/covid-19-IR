from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import csv
from nltk.tokenize import RegexpTokenizer
import joblib
from nltk.corpus import stopwords
import string
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentPoolEmbeddings, Sentence, ELMoEmbeddings,BertEmbeddings,DocumentRNNEmbeddings
import numpy as np

import sys

stopwords_flag=1

tokenizer = RegexpTokenizer(r'\w+') 

flair_embedding_backward = FlairEmbeddings('pubmed-backward')
flair_embedding_forward = FlairEmbeddings('pubmed-forward')
Bert_embedding=BertEmbeddings()
Glove_embedding = WordEmbeddings('glove')
#FastText
FastText_embedding = WordEmbeddings('en')
#document_embeddings = DocumentPoolEmbeddings([flair_embedding_backward,flair_embedding_forward])
#document_embeddings = DocumentPoolEmbeddings([Bert_embedding])
#document_embeddings = DocumentPoolEmbeddings([FastText_embedding])
document_embeddings = DocumentPoolEmbeddings([FastText_embedding])


#print(stopwords_english)
passages=True

in_file='metadata.csv_covid-19.kwrds.csv'
if passages:
    in_file='metadata.csv_covid-19.kwrds.paragraphs.csv'

with open(in_file) as tsvfile:    
    reader = csv.DictReader(tsvfile, dialect='excel')

    out_file = in_file+".fasttext-coords.csv"
    of=open(out_file,"w", encoding='utf-8')
    fieldnames=reader.fieldnames
    fieldnames.append('fasttext_coord_x')
    fieldnames.append('fasttext_coord_y')
    sys.stderr.write("fields: {}\n".format(fieldnames))
    wr=csv.DictWriter(of,fieldnames=fieldnames, dialect='excel')
    wr.writeheader()

    A = np.array([])
    
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


        #Remove stopwords?
        if stopwords_flag:
            tokens = tokenizer.tokenize(text)
            tokenak=[]
            for tok in tokens:
                #filter non alphanumeric tokens and stop words
                if not (tok in string.punctuation) and not(tok.isnumeric()) and not(tok.lower() in stopwords.words('english')) and (len(tok) > 1) :
                    tokenak.append(tok)
            tokenized_text=" ".join(tokenak)
            text=tokenized_text.lower()

        sentence = Sentence(text,use_tokenizer=True)
        #sentence.tokens = sentence.tokens[:100]        
        if len(sentence)>0:
            document_embeddings.embed(sentence)
            new_row=sentence.get_embedding().detach().numpy()
            #sys.stderr.write("row shape: {}\n".format(new_row.shape))
        else:
             new_row=np.zeros(300)
        if len(A)==0:
            A=new_row
        else:
            A = np.vstack((A, new_row))                                                                                                            
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

    #Dimension reduction
    tsne_model = TSNE(n_components=2, verbose=1, random_state=0)
    svd = TruncatedSVD(n_components=50, random_state=0)
    svd_A = svd.fit_transform(A)
    tsne_A = tsne_model.fit_transform(svd_A)

    for row in output:
        dokid='cord_uid'
        if passages:
            dokid='paragraph_id'
 
        row['fasttext_coord_x']=tsne_A[ids[row[dokid]]][0]
        row['fasttext_coord_y']=tsne_A[ids[row[dokid]]][1]
        
        wr.writerow(row)

    of.close()
#    joblib.dump(titles, 'covid_Titles.pkl')
#    joblib.dump(tsne_tfidf, 'covid_Tfidf_tsne.pkl')
#    joblib.dump(kats, 'covid_Names.pkl')
#    joblib.dump(vecfit, 'covid_Tfidfmodel.pkl')
#    joblib.dump(vec_trans, 'covid_Tfidf.pkl')
#    joblib.dump(abstracts, 'covid_abs.pkl')
    

