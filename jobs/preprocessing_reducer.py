#!/usr/bin/env python3

import sys
import csv

from collections import defaultdict

    
def reducer(input_stream, output_stream):
    token_count = defaultdict(lambda: defaultdict(int))
    
    for line in input_stream:
        key, token = line.strip().split('\t')
        token_count[key][token] += 1

    for key, tokens in token_count.items():
        output_stream.write(key)
        output_stream.write('\t')
        output_stream.write(','.join(k + ':' + str(v) for k, v in  tokens.items()))
        output_stream.write('\n')
    
    output_stream.flush()
    
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()