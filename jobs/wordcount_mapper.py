#!/usr/bin/env python3

import csv
import sys
import re

with open('stopwords.txt', 'r', encoding='utf-8') as f:
    STOPWORDS = set(f.read().splitlines())

def tokenize(content):
    tokens = [
        t.lower() for t in re.findall(r"(?u)\b[A-Za-zÀ-ÖØ-öø-ÿ]+\b", content) 
        if t.lower() not in STOPWORDS
    ]
    return tokens

def mapper(input_stream, output_stream):
    reader = csv.reader(input_stream, quoting=csv.QUOTE_ALL)

    for i, line in enumerate(reader):
        fake_or_real, content = line[3], line[6]
        for token in tokenize(content):
            output_stream.write(token)
            output_stream.write('\t')
            output_stream.write(fake_or_real)
            output_stream.write('\n')


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mapper(sys.stdin, sys.stdout)
sys.stdout.flush()