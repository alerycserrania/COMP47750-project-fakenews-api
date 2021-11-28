#!/usr/bin/env python3

import sys
import csv

def mapper(input_stream, output_stream):
    reader = csv.reader(input_stream, quoting=csv.QUOTE_MINIMAL)
    
    for _, real_count, fake_count in reader:
        output_stream.write('r\t' + str(real_count) + '\n')
        output_stream.write('f\t' + str(fake_count) + '\n')


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
mapper(sys.stdin, sys.stdout)
sys.stdout.flush()