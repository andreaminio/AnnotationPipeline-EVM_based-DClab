#!/usr/bin/env/ python

# arg 1 -> bast results
# std.log > unique ids
# std.err > clusters

import sys

hits = {}

#load

max_hits = ["",0]

# Parse blast hits
for line in open( sys.argv[1] ):
	candidate1, candidate2 , cov, iden = line.strip().split("\t")
        # Add blast hit to dictionary for both candidates
	if candidate1 not in hits.keys() :
		hits[candidate1]=[] 
	if candidate2 not in hits[candidate1]:
		hits[candidate1].append(candidate2)
	if candidate2 not in hits.keys() :
		hits[candidate2]=[]
	if candidate1 not in hits[candidate2]:                        
		hits[candidate2].append(candidate1)
        # Search for most abundant cluster
	if hits[candidate1].__len__() >= hits[candidate2].__len__() :
                # candidate1 represent a cluster more abundant, if it bigger tah the max found, upate max
		if hits[candidate1].__len__() > max_hits[1] : max_hits=[candidate1,hits[candidate1].__len__()]
	else:
		if hits[candidate2].__len__() > max_hits[1] : max_hits=[candidate2,hits[candidate2].__len__()]

while hits.keys().__len__()>0 :
        # Print the reprentative and the cluster
	representative = max_hits[0]
	cluster = hits[representative]
	print >> sys.stdout, representative
	print >> sys.stderr, "> " + representative
	print >> sys.stderr, "\t".join(cluster)
	print >> sys.stderr, ""

	max_hits=["",0]

        # Remove the cluster
	del hits[representative]
        # Remove all the clustered elements for the dictionary
	for element in cluster: 
                # as cluster representatives
		if element in hits.keys() :
			del hits[element]
                # as cluster elements
		for key in hits.keys() :
			if element in hits[key] :
				hits[key].remove(element)

        # Update most abundant cluster
	for key in hits.keys() :
		if hits[key].__len__() > max_hits[1] : max_hits=[key,hits[key].__len__()]
