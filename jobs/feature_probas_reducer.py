#!/usr/bin/env python3

import sys
import csv
import math
from hdfs import InsecureClient

path = sys.argv[1]
ALPHA = 1.0


def get_class_count_and_nb_words():
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])
    class_count = dict()
    with client.read(f'{path}/class_priors.csv', encoding='utf-8', ) as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        for cl, count, _ in reader:
            class_count[cl] = int(count)

    nb_words = 0
    with client.read(f'{path}/nb_words.txt', encoding='utf-8') as f:
        nb_words = int(f.read())
    
    return class_count, nb_words
    

def reducer(input_stream, output_stream):
    reader = csv.reader(input_stream, quoting=csv.QUOTE_MINIMAL)
    writer = csv.writer(output_stream, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    words_proba = dict()

    class_count, nb_words = get_class_count_and_nb_words()
    for word, real_count, fake_count in reader:
        words_proba[word] = {
            'r': math.log(int(real_count) + ALPHA) - math.log(class_count['r'] + nb_words*ALPHA),
            'f': math.log(int(fake_count) + ALPHA) - math.log(class_count['f'] + nb_words*ALPHA),
        }
    
    for word, probas in words_proba.items():
        writer.writerow([word, probas['r'], probas['f']])


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()