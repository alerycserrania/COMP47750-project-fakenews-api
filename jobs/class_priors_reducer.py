#!/usr/bin/env python3

from collections import defaultdict
import sys
import csv
import math
import os

from hdfs.client import InsecureClient

path = sys.argv[1]

def get_nb_articles():
    nb_articles = 0
    client = InsecureClient(os.environ['FASTAPI_HADOOP_WEB_URL'])
    with client.read(f'{path}/nb_articles.txt', encoding='utf-8') as f:
        nb_articles = int(f.read())
    
    return nb_articles

def reducer(input_stream, output_stream):
    writer = csv.writer(output_stream, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    nb_articles = get_nb_articles()
    cl_count = defaultdict(int)
    for line in input_stream:
        cl, count = line.strip().split('\t')
        cl_count[cl] += int(count)

    for cl, count in cl_count.items():
        writer.writerow([cl, count, math.log(count / nb_articles)])


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()