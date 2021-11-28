#!/usr/bin/env python3

import csv
import io
import sys
import re
from hdfs import InsecureClient

path = sys.argv[1]

with open('stopwords.txt', 'r', encoding='utf-8') as f:
    STOPWORDS = set(f.read().splitlines())

def tokenize(content):
    tokens = [
        t.lower() for t in re.findall(r"(?u)\b[A-Za-zÀ-ÖØ-öø-ÿ]+\b", content) 
        if t.lower() not in STOPWORDS
    ]
    return tokens

def get_feature_probas():
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])
    with client.read(f'{path}/feature_probas.csv', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        return {w: (float(p_real), float(p_fake)) for w, p_real, p_fake in reader}


def mapper(input_stream, output_stream):
    reader = csv.reader(input_stream, quoting=csv.QUOTE_ALL)
    feature_probas = get_feature_probas()

    for idx, line in enumerate(reader):
        content = line[6]
        for token in tokenize(content):
            if token in feature_probas:
                output_stream.write(str(idx))
                output_stream.write('\t')
                output_stream.write(str(feature_probas[token][0]))
                output_stream.write(' ')
                output_stream.write(str(feature_probas[token][1]))
                output_stream.write('\n')
        


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mapper(sys.stdin, sys.stdout)
sys.stdout.flush()