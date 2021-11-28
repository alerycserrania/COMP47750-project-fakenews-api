#!/usr/bin/env python3

from collections import defaultdict
import sys
import csv
from hdfs import InsecureClient

path = sys.argv[1]

def get_class_priors():
    class_priors = dict()
    client = InsecureClient('http://0.0.0.0:9870')
    with client.read(f'{path}/class_priors.csv', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        for cl, _, prior in reader:
            class_priors[cl] = float(prior)
    return class_priors

def reducer(input_stream, output_stream):
    writer = csv.writer(output_stream, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    products = defaultdict(lambda: (0, 0))
    for line in input_stream:
        key, value = line.strip().split('\t')
        pr, pf = [float(p) for p in value.split()]
        products[key] = (
            products[key][0] + pr,
            products[key][1] + pf
        )

    class_priors = get_class_priors()
    for key in products:
        products[key] = (
            products[key][0] + class_priors['r'],
            products[key][1] + class_priors['f']
        )
        writer.writerow([int(key), 'r' if products[key][0] > products[key][1] else 'f', *products[key]])


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()