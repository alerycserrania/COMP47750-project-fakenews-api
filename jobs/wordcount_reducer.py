#!/usr/bin/env python3

import sys
import csv

from collections import defaultdict

    
def reducer(input_stream, output_streamer):
    token_count = defaultdict(lambda: [0, 0])
    writer = csv.writer(output_streamer, quoting=csv.QUOTE_MINIMAL,  lineterminator='\n')
    
    for line in input_stream:
        word, fake_or_real = line.strip().split('\t')
        if fake_or_real == 'r':
            token_count[word][0] += 1
        elif fake_or_real == 'f':
            token_count[word][1] += 1

    for key, (real_count, fake_count) in token_count.items():
        writer.writerow([key, real_count, fake_count])
    
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()