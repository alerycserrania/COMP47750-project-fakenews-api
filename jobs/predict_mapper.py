#!/usr/bin/env python3

import csv
import sys
import os
from hdfs import InsecureClient

path = sys.argv[1]

def get_feature_probas():
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])
    with client.read(f'{path}/feature_probas.csv', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        return {w: (float(p_real), float(p_fake)) for w, p_real, p_fake in reader}


def mapper(input_stream, output_stream):
    feature_probas = get_feature_probas()

    for line in input_stream:
        key, value = line.strip().split('\t')
        for token_count in value.split(','):
            token, count = token_count.split(':')
            if token in feature_probas:  
                for _ in range(int(count)):
                    output_stream.write(str(key.split()[0]))
                    output_stream.write('\t')
                    output_stream.write(str(feature_probas[token][0]))
                    output_stream.write(' ')
                    output_stream.write(str(feature_probas[token][1]))
                    output_stream.write('\n')
        


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mapper(sys.stdin, sys.stdout)
sys.stdout.flush()