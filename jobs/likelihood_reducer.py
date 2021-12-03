#!/usr/bin/env python3

import sys
import csv
import math
import os
from hdfs import InsecureClient
from collections import defaultdict

path = sys.argv[1]
ALPHA = 1.0


def get_class_count_and_vocab_size():
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])
    class_count = dict()
    with client.read(f'{path}/class_priors.csv', encoding='utf-8', ) as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        for cl, count, _ in reader:
            class_count[cl] = int(count)

    vocab_size = 0
    with client.read(f'{path}/vocab_size.txt', encoding='utf-8') as f:
        vocab_size = int(f.read())
    
    return class_count, vocab_size
    

def reducer(input_stream, output_stream):
    writer = csv.writer(output_stream, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    words_likel = defaultdict(lambda: [0, 0])
    class_count, vocab_size = get_class_count_and_vocab_size()

    for line in input_stream:
        token, val = line.strip().split('\t')
        fake_or_real, count = val.split()
        if fake_or_real == 'r':
            words_likel[token][0] += int(count)
        elif fake_or_real == 'f':
            words_likel[token][1] += int(count)

    
    for word, (real_count, fake_count) in words_likel.items():
        writer.writerow([
            word, 
            math.log(real_count + ALPHA) - math.log(class_count['r'] + ALPHA * vocab_size), 
            math.log(fake_count + ALPHA) - math.log(class_count['f'] + ALPHA * vocab_size)
        ])


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()