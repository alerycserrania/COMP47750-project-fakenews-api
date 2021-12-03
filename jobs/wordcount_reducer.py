#!/usr/bin/env python3

from collections import defaultdict
import sys
import csv

    
def reducer(input_stream, output_stream):
    writer = csv.writer(output_stream, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    token_count = defaultdict(lambda: [0, 0])
    for line in input_stream:
        token, val = line.strip().split('\t')
        fake_or_real, count = val.split()
        if fake_or_real == 'r':
            token_count[token][0] += int(count)
        elif fake_or_real == 'f':
            token_count[token][1] += int(count)

    for token, (real_count, fake_count) in token_count.items():
        writer.writerow([token, real_count, fake_count])
        
    
    output_stream.flush()
    
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()