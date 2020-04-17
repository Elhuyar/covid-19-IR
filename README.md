# covid-19-IR

**Wide perspective query system focused on COVID-19
**

System that offers integral consultation of scientific papers on COVID-19 through search at document and passage level and with auxiliary visualization of the results.

Developed for the [CORD-19](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/) challenge.

Kaggle notebook available at : https://www.kaggle.com/isanvi/covid-19-ir-system-elhuyar

Also there is an initial interactive demo that provides navigation of the challenge questions and results at http://covid19kaggle.elhuyar.eus/


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


## Dependencies
* python 3.6+ required (tested with 3.6.9)
* [Indri](https://www.lemurproject.org/indri.php) - Latest version can be found at (https://sourceforge.net/projects/lemur/files/lemur/)
* [BERT](https://github.com/google-research/bert)
* [Flair] (https://github.com/zalandoresearch/flair)

All Python dependencies are automatically install by creating a virtual environment using the venv.requirements file provided here.


# Script guide (ongoing work)
Scripts order:

1 - Filter papers talking about covid-19:
'''shell
src/filter_dataset_with_kwords.py
'''

2 - Generate document and passage vectorial representation and their coordinates in a 2d space.

3 - Fine tuning for passage reranking
3.1 - Prepare dataset for finetuning:
'''shell
src/createPassagePseuTrain-reranking.py
'''
3.2 - Finetuning

4 - Index collections with Indri

5 - Retrieval

6 - Visualization



