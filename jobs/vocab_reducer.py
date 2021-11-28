#!/usr/bin/env python3

import sys
import csv

def reducer(input_stream, output_stream):
    reader = csv.reader(input_stream, quoting=csv.QUOTE_MINIMAL)
    output_stream.write(str(sum([1 for _ in reader])))


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()