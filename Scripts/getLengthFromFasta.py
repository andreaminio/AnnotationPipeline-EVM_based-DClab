#!/usr/bin/env python

import sys
from Bio import SeqIO

for record in SeqIO.parse(open(sys.argv[1]), 'fasta'):
	print >> sys.stdout, record.id + "\t" + str(len(record))
