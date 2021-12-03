#!/usr/bin/env python3

import sys

def mapper(input_stream, output_stream):
    for line in input_stream:
        output_stream.write('1\t' + line)
    output_stream.flush()


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mapper(sys.stdin, sys.stdout)
sys.stdout.flush()