import pyndri
from nltk.tokenize import RegexpTokenizer

index = pyndri.Index('./BildumaIndex')
query="hello world"
tokenizer = RegexpTokenizer(r'\w+')
querylc = query.lower()
tokens = tokenizer.tokenize(querylc)        
tokenized_query=" ".join(tokens)

results = index.query(tokenized_query, results_requested=50)
for int_document_id, score in results:
    ext_document_id, _ = index.document(int_document_id)
    print(ext_document_id, score)
