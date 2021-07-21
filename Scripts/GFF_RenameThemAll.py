#!/usr/bin/env python
#### Usage: GFF_RenameThemAll.py new_id version_number chr_name old.gff > new.gff 2> conversion.log

#### Argv 1 = string of new ID
#### Argv 2 = Version number
#### Argv 3 = CHR name to strip
#### Argv 4 = file GFF


import sys
from operator import itemgetter

gene_digits = 6
ver_digits = 1
mrna_digits = 2
chr_digits = 3

new_name = sys.argv[1]
version = sys.argv[2]
chr_name = sys.argv[3]

print >> sys.stdout, "##gff-version 3"

to_sort = ""

genes = {}

mRNA = {}

dandling_mRNA = {}

mRNA_feat_order = {"exon": 1, "intron":1, "five_prime_UTR": 2, "CDS": 3, "three_prime_UTR": 4}

##### Read GFF #####

for line in open(sys.argv[4]):
	#print >> sys.stderr, line.rstrip().rstrip(";").split("\t")
	if line[0] == "#" or line.rstrip().rstrip(";") == "":
		continue
	else:
		attributes_dict = {}
		seqname, source, feature, start, end, score, strand, frame, attribute = line.rstrip().rstrip(";").split("\t")
		#print >> sys.stdout, attribute
		for chunk in attribute.rstrip(";").split(";"):
			att = chunk.split("=")
			#print >> sys.stdout, att
			attributes_dict[att[0]] = att[1]

		if feature == "gene" or feature == "intergenic" :
			gene_name = attributes_dict["ID"]
			if gene_name in genes :
				genes[gene_name][0] = line.rstrip().rstrip(";")
				genes[gene_name][1] = seqname
				genes[gene_name][2] = int(start)
			else:
				genes[gene_name] = [line.rstrip().rstrip(";"), seqname, int(start), {}]

		elif feature == "mRNA":
			gene_name = attributes_dict["Parent"]
			mRNA[attributes_dict["ID"]] = gene_name
			if gene_name in genes :
				genes[gene_name][3][attributes_dict["ID"]] = [line.rstrip().rstrip(";"), int(start), {}]
			else :
				genes[gene_name] = ["", "", "", {}]
				genes[gene_name][3][attributes_dict["ID"]] = [line.rstrip().rstrip(";"), int(start), {}]

		else :
			mRNA_ID = attributes_dict["Parent"]
			if mRNA_ID in mRNA :
				gene_name = mRNA[mRNA_ID]
				if attributes_dict["ID"] in genes[gene_name][3][mRNA_ID][2] :
					num = 0
					while attributes_dict["ID"] + "_" + str(num) in genes[gene_name][3][mRNA_ID][2].keys() : num += 1
					attributes_dict["ID"] = attributes_dict["ID"] + "_" + str(num)
					new_attribute = ""
					for key in attributes_dict.keys() : new_attribute = new_attribute + key + "=" + attributes_dict[key] + ";"
					new_line = "\t".join([seqname, source, feature, start, end, score, strand, frame, new_attribute])
				else : new_line = line.rstrip().rstrip(";")
				genes[gene_name][3][mRNA_ID][2][attributes_dict["ID"]] = [new_line.rstrip(";"), int(start), mRNA_feat_order[feature]]
			else :
				dandling_mRNA[mRNA_ID] = {}
				dandling_mRNA[mRNA_ID][attributes_dict["ID"]] = line.rstrip().rstrip(";")

##### Place dandling features where possible #####

err_file = open("dandling_features.txt", "a")
print >> err_file, "### Missing mRNA annotation for: ###"

if dandling_mRNA.keys().__len__() > 0 :
	for mRNA_ID in dandling_mRNA.keys() :
		if mRNA_ID in mRNA :
			mRNA[mRNA_ID] = gene_name
			for feat_name in dandling_mRNA[mRNA_ID].keys() :
				#print >> sys.stderr, dandling_mRNA[mRNA_ID][feat_name]
				seqname, source, feature, start, end, score, strand, frame, attribute = dandling_mRNA[mRNA_ID][feat_name].split("\t")
				for chunk in attribute.split(";"):
					att = chunk.split("=")
					attributes_dict[att[0]] = att[1]
				genes[gene_name][3][mRNA_ID][2][attributes_dict["ID"]] = [dandling_mRNA[mRNA_ID][feat_name], int(start), mRNA_feat_order[feature]]
		else :
			print >> err_file, mRNA_ID


##### PRINT #####

#sys.stderr   = open(feat_name + ".sys.stderr  .txt", "w")
print >> sys.stderr  , "Feture_type\tNew_ID\tOLD_ID"

gene_count = 100

# Iterate on genes

for g_key, g_value in sorted(genes.iteritems(), key=lambda (k, v): itemgetter(1, 2)(v)) :

	old_line = genes[g_key][0]
	seqname, source, feature, start, end, score, strand, frame, attribute = old_line.split("\t")

	if feature == "intergenic" :
		print >> sys.stdout, "### "
		print >> sys.stdout, old_line
		print >> sys.stderr  , "------"
		print >> sys.stderr  , "intergenic\t" + attribute.split("=")[1] + "\t" + attribute.split("=")[1]
		continue

	old_gene_id = g_key
	new_gene_id = new_name + genes[g_key][1].lstrip(chr_name)  + ".ver" + version.zfill(ver_digits) + ".g" + str(gene_count).zfill(gene_digits)
	print >> sys.stdout, "### " + new_gene_id
	print >> sys.stderr  , "------"
	print >> sys.stderr  , "gene\t" + new_gene_id + "\t" + old_gene_id
	#print >> sys.stderr  , genes[g_key]

	new_attributes_dict = {}
	att_order = []
	#print >> sys.stderr  , attribute.rstrip(";").split(";")
	for chunk in attribute.rstrip(";").split(";"):
		att = chunk.split("=")
		#print >> sys.stderr , att
		att_order.append(att[0])
		if att[0] == "ID" or att[0] == "Name" :
			new_attributes_dict[att[0]] = new_gene_id
		else :
			new_attributes_dict[att[0]] = att[1]
	#print att_order
	new_attribute_line = ""
	for key in att_order : new_attribute_line = new_attribute_line + key + "=" + new_attributes_dict[key] + ";"
	new_line = "\t".join([seqname, source, feature, start, end, score, strand, frame, new_attribute_line.rstrip(";")])

	print >> sys.stdout, new_line

	# Iterate on mRNAs
	mrna_count = 1

	for m_key, m_value in sorted(genes[g_key][3].iteritems(), key=lambda (k, v): itemgetter(1)(v)) :

		old_mrna_id = m_key
		new_mrna_id = new_gene_id + ".t" + str(mrna_count).zfill(mrna_digits)

		print >> sys.stderr  , "mrna\t" + new_mrna_id + "\t" + old_mrna_id

		old_line = genes[g_key][3][m_key][0]

		seqname, source, feature, start, end, score, strand, frame, attribute = old_line.split("\t")

		new_attributes_dict = {}
		att_order = []
		for chunk in attribute.split(";"):
			att = chunk.split("=")
			#print att[0]
			att_order.append(att[0])
			if att[0] == "ID" or att[0] == "Name" :
				new_attributes_dict[att[0]] = new_mrna_id
			else :
				if att[0] == "Parent" :
					new_attributes_dict[att[0]] = new_gene_id
				else :
					new_attributes_dict[att[0]] = att[1]

		new_attribute_line = ""
		for key in att_order: new_attribute_line = new_attribute_line + key + "=" + new_attributes_dict[key] + ";"
		new_line = "\t".join([seqname, source, feature, start, end, score, strand, frame, new_attribute_line.rstrip(";")])
		print >> sys.stdout, new_line


		# Iterate on mRNA features
		prev_feats = {}
		for feat_key, feat_value in sorted(genes[g_key][3][m_key][2].iteritems(), key=lambda (k, v) : itemgetter(2, 1)(v)) :
			old_feat_id = feat_key
			old_line = genes[g_key][3][m_key][2][feat_key][0]
			seqname, source, feature, start, end, score, strand, frame, attribute = old_line.split("\t")

			if feature in prev_feats :
				prev_feats[feature]+=1
			else:
				prev_feats[feature]=1

			new_feat_id = new_mrna_id + "." + feature + "_" + str(prev_feats[feature])
			print >> sys.stderr  , feature + "\t" + new_feat_id + "\t" + old_feat_id

			new_attributes_dict = {}
			att_order = []
			for chunk in attribute.split(";"):
				att_order = []
				att = chunk.split("=")
				#print att[0]
				att_order.append(att[0])
				if att[0] == "ID" or att[0] == "Name" :
					new_attributes_dict[att[0]] = new_feat_id
				else :
					if att[0] == "Parent" :
						new_attributes_dict[att[0]] = new_mrna_id
					else:
						new_attributes_dict[att[0]] = att[1]

			new_attribute_line = ""

			for key in new_attributes_dict.keys() : new_attribute_line = new_attribute_line + key + "=" + new_attributes_dict[key] + ";"

			new_line = "\t".join([seqname, source, feature, start, end, score, strand, frame, new_attribute_line.rstrip(";")])

			print >> sys.stdout, new_line

		mrna_count += 1
		print >> sys.stderr  , ""

	gene_count += 10
	print >> sys.stderr  , ""