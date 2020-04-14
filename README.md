# covid-19-IR

**Wide perspective query system focused on COVID-19
**

System that offers integral consultation of scientific papers on COVID-19 through search at document and passage level and with auxiliary visualization of the results.

Kaggle notebook available at : https://www.kaggle.com/isanvi/covid-19-ir-system-elhuyar


The system has the following features:
* Simultaneous and complementary retrieval of documents (coarse grain) and passages (fine grain) relevant to queries.
* Visual representation of relevant documents and paragraphs according to their semantic content.
* Hybrid retrieval of paragraphs and answers.

Techniques:
* Recovery of documents through language models (Indri).
* Recovery of passages by combining language models (Indri) and re-ranking based on fine-tuned BERT.
* Visualization by means of embeddings and reduction of dimensions.

Contributions:
* Results and visualization according to different techniques that offer an enriched and wide perspective consultation.
* Fine-tuning by trainset built from titles and abstracts.



python 3.6+ required (tested with 3.6.9)

Scripts order:

1 - Filter papers talking about covid-19:
'''shell
src/filter_dataset_with_kwords.py
'''

2 - Prepare dataset for finetuning:
'''shell
src/createPassagePseuTrain-reranking.py
'''


