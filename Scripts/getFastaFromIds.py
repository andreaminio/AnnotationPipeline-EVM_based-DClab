#!/usr/bin/env python

from __future__ import print_function
import sys, argparse, os
from Bio import SeqIO


def main():

	def check_type(string):
		if os.path.exists(string) and not os.path.isdir(string): return open(string)
		else: return set(string.split(','))

	parser = argparse.ArgumentParser(description='A simple script that retrieves the FASTA sequences from a file given a list of ids.')
	parser.add_argument("-v", "--reverse", action="store_true", default=False, help="Retrieve entries which are not in the list, as in grep -v (a homage).")
	parser.add_argument('list', type=check_type, help='File with the list of the ids to recover, one by line. Alternatively, names separated by commas.')
	parser.add_argument('fasta', type=argparse.FileType('r'), help='FASTA file.')
	parser.add_argument('out', type=argparse.FileType('w'), help='Optional output file.', nargs='?', default=sys.stdout)
	args = parser.parse_args()

	if isinstance(args.list, file):
		ids = set([line.rstrip() for line in args.list.readlines()])
	else: ids = args.list
	for record in SeqIO.parse(args.fasta, 'fasta'):
		if record.id in ids:
			if args.reverse: continue
			print(record.format('fasta'), file=args.out, end='')
			ids.remove(record.id)
			if len(ids) == 0 and not args.reverse: break
		else:
			if args.reverse:
				print(record.format('fasta'), file=args.out, end='')

if __name__ == '__main__': main()
