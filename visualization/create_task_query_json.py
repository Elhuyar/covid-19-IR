import json
import argparse


def main(fpath):
    with open(fpath, 'r') as f:
        data = json.load(f)
    tasks = {}
    for query in data:
        query_id = query['query_id']
        query_text = query['query']
        task_id = query['task']
        if task_id not in tasks:
            tasks[task_id] = []
        tasks[task_id].append({'id': query_id, 'title': query_text})
    print(json.dumps(tasks, indent=4))
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", required=True, help='JSON with all data')
    args = parser.parse_args()
    main(args.data)
