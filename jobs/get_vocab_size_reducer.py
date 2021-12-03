#!/usr/bin/env python3

import sys

def reducer(input_stream, output_stream):
    words = set()
    for line in input_stream:
        _, val = line.strip().split('\t')[1:]
        for token_count in val.split(','):
            words.add(token_count.split(':')[0])
    output_stream.write(str(len(words)))
    output_stream.flush()


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()