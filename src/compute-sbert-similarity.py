from sklearn.metrics.pairwise import cosine_similarity
from numpy import dot
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer
import csv
import sys


rerank_csv="rerank-queries-3500.tsv"
i_f=open(rerank_csv,"r", encoding='utf-8')
fieldnames=["question", "question_id","answer","answer_id","label"]
candidates=csv.DictReader(i_f,fieldnames=fieldnames, dialect='excel-tab')
#wr.writeheader()     

rerank_csv="rerank-scores-query-narrative-3500-sbert-large.tsv"
of=open(rerank_csv,"w", encoding='utf-8')
fieldnames=["query_candidate_id", "label","neg_score","pos_score"]
wr=csv.DictWriter(of,fieldnames=fieldnames, dialect='excel-tab')
wr.writeheader()     



model = SentenceTransformer('bert-large-nli-mean-tokens')

count=0
for c in candidates:
    count+=1
    sys.stderr.write("\r processed {} candidates ".format(count))
    sentence1 = [c["question"]]
    sentence1_embedding = model.encode(sentence1)[0]
    sentence2 = [c["answer"]]
    sentence2_embedding = model.encode(sentence2)[0]
    cos_sim = dot(sentence1_embedding,sentence2_embedding)/(norm(sentence1_embedding)*norm(sentence2_embedding))
    cid="q-"+c["question_id"]+"-"+c["answer_id"]

    wr.writerow({"query_candidate_id":cid, "label":0,"neg_score":0,"pos_score":cos_sim})

i_f.close()
of.close()
