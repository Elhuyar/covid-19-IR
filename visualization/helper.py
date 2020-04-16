import json
import random
import math

def parse_json(fpath):
    queries = []
    with open(fpath, 'r') as f:
        queries_j = json.load(f)
        for query_j in queries_j:
            query = {
                'id': query_j['query_id'],
                'title': query_j['query'],
                'task': query_j['task'],
                'docs': [],
                'pas': []
            }
            query['docs'] = parse_entries(query_j['docs'])
            query['pas'] = parse_entries(query_j['pas'])
            queries.append(query)
    return queries
    

def parse_entries(entries):
    _ents = []
    for entry in entries:
        _ent = {
            'doc_id': entry['doc_id'],
            'score': entry['ranking_score'],
            'title': entry['title'],
            'coord_x': entry['coordinates']['coord_x'],
            'coord_y': entry['coordinates']['coord_y'],
            'text': entry['text'] if type(entry['text'])==str else "",
            'authors': entry['author'] if type(entry['author'])==str else "",
            'journal': entry['journal'] if type(entry['journal'])==str else "",
            'url': entry['url'] if type(entry['url'])==str else "",
            'date': entry['publish_date'],
        }
        _ents.append(_ent)
        _ents.sort(key=lambda p: p['score'], reverse=True)
    return _ents
