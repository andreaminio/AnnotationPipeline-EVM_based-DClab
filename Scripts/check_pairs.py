#!/usr/bin/env python

import sys
import itertools
import argparse

###### Options and help ######

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--chain", dest="chain",
				help="File of perfectly matching chains", metavar="perfect_chains.txt [Required]")
parser.add_argument("-p", "--pairs", dest="pairs",
				help="Output NAME prefix for files [default: out]", metavar="perfect_CDS_matches.txt [Required]")

if len(sys.argv) < 2:
	parser.print_help()
	sys.exit(1)

options = parser.parse_args()

if not options.chain :
	print >> sys.stderr , "[ERROR] Input perfectly matching chains missing"
	parser.print_help()
	sys.exit(1)

if not options.pairs :
	print >> sys.stderr , "[ERROR] Input perfectly matching CDSs missing"
	parser.print_help()
	sys.exit(1)

###### Main ######

# Read CDS match pairs
CDS_pairs = {}
pairs=0
print >> sys.stderr , "Reading matching CDS pairs"
for line in open(options.pairs) :
	t1 , t2 = line.rstrip().split("\t")
	if ( t1 , t2 ) not in CDS_pairs :
		CDS_pairs[ ( t1 , t2 ) ] = ( t1 , t2 )
		CDS_pairs[ ( t2 , t1 ) ] = ( t2 , t1 )
		pairs+=1

print >> sys.stderr , "### Found " + str(pairs) + " CDS pairs"


# Read Chains, check pairs and output table
print >> sys.stderr , "Reading matching intron chains"
for line in open(options.chain) :
	match = line.rstrip().split("\t")

	new_line = [ match[0] ]

	ids = match[1:]
	for pair in itertools.combinations(ids,2) :
		if (pair[0],pair[1]) in CDS_pairs :
			new_line.append(pair[0]+"|"+pair[1]+":TRUE")
		else :
			new_line.append(pair[0]+"|"+pair[1]+":FALSE")

	print >> sys.stdout, "\t".join(new_line)