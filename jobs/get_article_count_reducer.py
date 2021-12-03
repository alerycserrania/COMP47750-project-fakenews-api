#!/usr/bin/env python3

import sys

def reducer(input_stream, output_stream):
    output_stream.write(str(sum(int(n.strip().split('\t')[0]) for n in input_stream)))
    output_stream.flush()


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()