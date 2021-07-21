#!/usr/bin/env python

import sys
import pysam
from array import *
import argparse
import gc
import os
import pipes

gc.garbage.append(sys.stdout)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

###### Options and help ######

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sam", dest="sam_in",
				help="Input raw alignments (SAM format)", metavar="in.sam [Required]")
parser.add_argument("-o", "--output", dest="sam_out", default="out.sam",
				help="Output filtered alignments.", metavar="out.sam [default]")
parser.add_argument("-c", "--coverage", dest="cov", default="80",
				help="Output filtered alignments.", metavar="N [default: 80]")
parser.add_argument("-i", "--identity", dest="iden", default="80",
				help="Output filtered alignments.", metavar="N [default: 80]")

if len(sys.argv) < 2:
	parser.print_help()
	sys.exit(1)

options = parser.parse_args()

if not options.sam_in :
	print >> sys.stderr , "[ERROR] missing input alignments"
	parser.print_help()
	sys.exit(1)

samfile_in = pysam.AlignmentFile(options.sam_in,"r")
samfile_out = pysam.AlignmentFile(options.sam_out,"w", template=samfile_in)
cov_thr = float(options.cov)
iden_thr = float(options.iden)

print >> sys.stderr , "\t".join(["Q_ID","Q_START","Q_STOP","T_ID","T_START","T_STOP","Q_LEN","ALN_LEN","REF_ALN_REGION_LEN","COV","IDEN1"])

kept = 0
rejected = 0

for read in samfile_in.fetch():

	#print >> sys.stderr , len(read.get_cigar_stats())
	m = read.get_cigar_stats()[0][0]
	cov = float(100*m)/float(read.query_alignment_length)
	iden = float(read.query_alignment_length*100)/float(read.query_length)

	if cov >= cov_thr and iden >= iden_thr :
		keep = "KEEP"
		kept += 1
	else :
		keep = "REJECT"
		rejected += 1

	if keep == "KEEP":
		samfile_out.write(read)

	print >> sys.stderr , read.query_name + "\t" + str(read.query_alignment_start) + "\t" + str(read.query_alignment_end) + "\t" + read.reference_name + "\t" + str(read.reference_start) + "\t" + str(read.reference_end) + "\t" + str(read.query_length) + "\t" + str(read.query_alignment_length)+ "\t" + str(read.reference_end - read.reference_start) + "\t" +  str(cov)  + "\t" + str(iden) + "\t" + str(keep)

print >> sys.stdout, "Total alignments:    " + str(kept + rejected)
print >> sys.stdout, "Kept alignments:     " + str(kept)
print >> sys.stdout, "Rejected alignments: " + str(rejected)