from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
import csv
import joblib
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentPoolEmbeddings, Sentence, ELMoEmbeddings,BertEmbeddings,DocumentRNNEmbeddings
import string
import numpy as np
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords



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


with open('MetadataFiltered.csv') as tsvfile:    
    reader = csv.reader(tsvfile, delimiter='\t',quotechar='"')
    #Dont print header
    next(reader)    
    A = np.array([])
    texts=[]
    kats=[]
    for row in reader:        
        dokid=row[0]
        title=row[1]
        abstract=row[2]
        text=title+" "+abstract
        print(str(len(text)))

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
            print(text)
        sentence = Sentence(text,use_tokenizer=True)
        #sentence.tokens = sentence.tokens[:100]        
        if len(sentence)>0:
            document_embeddings.embed(sentence)
            new_row=sentence.get_embedding().detach().numpy()        
        else:
             new_row=np.zeros(350)
        if len(A)==0:
            A=new_row
        else:
            A = np.vstack((A, new_row))                                                                                                                 

        #Dokids list
        kats.append(dokid)
                

    #Dimension reduction
    tsne_model = TSNE(n_components=2, verbose=1, random_state=0)
    svd = TruncatedSVD(n_components=50, random_state=0)
    svd_A = svd.fit_transform(A)
    tsne_A = tsne_model.fit_transform(svd_A)
                        
        
    #joblib.dump(kats, 'covid_Names_bert.pkl')
    #joblib.dump(A, 'covid_Densemodel_bert.pkl')

                                         
