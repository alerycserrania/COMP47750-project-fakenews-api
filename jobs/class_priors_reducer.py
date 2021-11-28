#!/usr/bin/env python3

from collections import defaultdict
import sys
import csv
import math

def reducer(input_stream, output_stream):
    writer = csv.writer(output_stream, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    cl_count = defaultdict(int)
    sum_cl = 0
    for line in input_stream:
        cl, count = line.strip().split('\t')
        cl_count[cl] += int(count)
        sum_cl += int(count)

    for cl, count in cl_count.items():
        writer.writerow([cl, count, math.log(count / sum_cl)])


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
reducer(sys.stdin, sys.stdout)
sys.stdout.flush()