#!/usr/bin/env python3

import sys

    
def mapper(input_stream, output_stream):
    for line in input_stream:
        key, val = line.strip().split('\t')
        for token_count in val.split(','):
            token, count = token_count.split(':')
            output_stream.write(token)
            output_stream.write('\t')
            output_stream.write(key.split()[1] + ' ' + count)
            output_stream.write('\n')
    
    output_stream.flush()
    
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mapper(sys.stdin, sys.stdout)
sys.stdout.flush()